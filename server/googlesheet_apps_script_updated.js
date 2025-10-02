// Google Apps Script (doPost)
// このコードをGoogle Apps Scriptエディタに貼り付けてデプロイしてください
//
// デプロイ手順:
// 1. https://script.google.com/ にアクセス
// 2. 新しいプロジェクトを作成（または既存のプロジェクトを開く）
// 3. このコードを貼り付け
// 4. 「デプロイ」→「新しいデプロイ」→「ウェブアプリ」を選択
// 5. 「次のユーザーとして実行」→「自分」を選択
// 6. 「アクセスできるユーザー」→「全員」を選択
// 7. デプロイ後、ウェブアプリのURLをコピー
// 8. .envファイルのGAS_WEBHOOK_URLに設定

function doPost(e) {
  try {
    if (!e.postData || !e.postData.contents) {
      return ContentService.createTextOutput(JSON.stringify({ok: false, error: 'no data'}))
             .setMimeType(ContentService.MimeType.JSON);
    }

    var payload = JSON.parse(e.postData.contents);

    // 簡易的なシークレット確認（セキュリティ強化）
    var SHARED_SECRET = 'oekaki_battler_line_to_gas_secret_shiyow5'; // ← .envのSHARED_SECRETと一致させる
    if (!payload.secret || payload.secret !== SHARED_SECRET) {
      return ContentService.createTextOutput(JSON.stringify({ok: false, error: 'forbidden'}))
             .setMimeType(ContentService.MimeType.JSON);
    }

    // アクションタイプを確認
    var action = payload.action || 'upload';

    // 削除リクエストの場合
    if (action === 'delete') {
      return handleDelete(payload);
    }

    // 手動入力でキャラクター登録
    if (action === 'register_character_manual') {
      return handleRegisterCharacterManual(payload);
    }

    // AI自動生成でキャラクター登録
    if (action === 'register_character_auto') {
      return handleRegisterCharacterAuto(payload);
    }

    // アップロードリクエストの場合（デフォルト）
    var b64 = payload.image;
    var mime = payload.mimeType || 'image/jpeg';
    var filename = payload.filename || ('upload_' + new Date().getTime() + '.jpg');

    // Base64 をデコードして blob を作成
    var blob = Utilities.newBlob(Utilities.base64Decode(b64), mime, filename);

    // Drive に保存（フォルダIDを指定）
    var folderId = '1JT7QnTcSrLo2AC4p580V7fa_MScuVd4G'; // ← あなたのDriveフォルダID
    var file;
    if (folderId) {
      var folder = DriveApp.getFolderById(folderId);
      file = folder.createFile(blob);
    } else {
      file = DriveApp.createFile(blob);
    }

    // 共有リンク（誰でも閲覧に設定）
    file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);

    // 直接ダウンロード可能なURLを生成
    var fileId = file.getId();
    var directUrl = 'https://drive.google.com/uc?export=view&id=' + fileId;

    // LINE Bot経由の場合のみスプレッドシートに記録
    if (payload.source === 'linebot') {
      var ssId = '1asfRGrWkPRszQl4IUDO20o9Z7cgnV1bEVKVNt6cmKfM'; // スプレッドシートID
      var ss = SpreadsheetApp.openById(ssId);
      var sheet = ss.getSheetByName('Sheet1') || ss.getSheets()[0];
      var now = new Date();
      sheet.appendRow([now, filename, directUrl]);

      // 画像をシートに貼り付け（オプション）
      var lastRow = sheet.getLastRow();
      try {
        sheet.insertImage(file.getBlob(), 4, lastRow);
      } catch (err) {
        console.warn('insertImage failed:', err);
      }
    }

    return ContentService.createTextOutput(JSON.stringify({
      ok: true,
      url: directUrl,
      fileId: fileId,
      filename: filename
    })).setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({
      ok: false,
      error: err.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

// ファイル削除ハンドラー
function handleDelete(payload) {
  try {
    var fileId = payload.fileId;

    if (!fileId) {
      return ContentService.createTextOutput(JSON.stringify({
        ok: false,
        error: 'fileId is required for delete action'
      })).setMimeType(ContentService.MimeType.JSON);
    }

    // DriveからファイルIDでファイルを取得して削除
    var file = DriveApp.getFileById(fileId);
    file.setTrashed(true); // ゴミ箱に移動

    return ContentService.createTextOutput(JSON.stringify({
      ok: true,
      message: 'File deleted successfully',
      fileId: fileId
    })).setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({
      ok: false,
      error: err.toString(),
      fileId: payload.fileId || 'unknown'
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

// 手動入力でキャラクター登録
function handleRegisterCharacterManual(payload) {
  try {
    var imageUrl = payload.imageUrl;
    var fileId = payload.fileId;
    var characterData = payload.characterData;

    if (!imageUrl || !characterData) {
      return ContentService.createTextOutput(JSON.stringify({
        ok: false,
        error: 'imageUrl and characterData are required'
      })).setMimeType(ContentService.MimeType.JSON);
    }

    // スプレッドシートにキャラクターを登録
    var ssId = '1asfRGrWkPRszQl4IUDO20o9Z7cgnV1bEVKVNt6cmKfM'; // スプレッドシートID
    var ss = SpreadsheetApp.openById(ssId);
    var sheet = ss.getSheetByName('Characters') || ss.getSheets()[0];

    // 新しいIDを生成（最終行+1）
    var lastRow = sheet.getLastRow();
    var newId = lastRow; // ヘッダー行を考慮

    var now = new Date();

    // キャラクターデータを追加
    // 列: ID, Name, Image URL, Sprite URL, HP, Attack, Defense, Speed, Magic, Description, Created At, Wins, Losses, Draws
    sheet.appendRow([
      newId,
      characterData.name,
      imageUrl,
      imageUrl, // スプライトURLは元画像と同じ（後でPythonで処理可能）
      characterData.hp,
      characterData.attack,
      characterData.defense,
      characterData.speed,
      characterData.magic,
      characterData.description,
      now,
      0, // Wins
      0, // Losses
      0  // Draws
    ]);

    return ContentService.createTextOutput(JSON.stringify({
      ok: true,
      message: 'Character registered successfully (manual)',
      character: {
        id: newId,
        name: characterData.name,
        hp: characterData.hp,
        attack: characterData.attack,
        defense: characterData.defense,
        speed: characterData.speed,
        magic: characterData.magic,
        description: characterData.description
      }
    })).setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({
      ok: false,
      error: err.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

// AI自動生成でキャラクター登録
function handleRegisterCharacterAuto(payload) {
  try {
    var imageUrl = payload.imageUrl;
    var fileId = payload.fileId;

    if (!imageUrl) {
      return ContentService.createTextOutput(JSON.stringify({
        ok: false,
        error: 'imageUrl is required'
      })).setMimeType(ContentService.MimeType.JSON);
    }

    // スプレッドシートにキャラクターを登録（ステータスは空）
    // Pythonアプリ起動時にAI分析して自動生成される
    var ssId = '1asfRGrWkPRszQl4IUDO20o9Z7cgnV1bEVKVNt6cmKfM'; // スプレッドシートID
    var ss = SpreadsheetApp.openById(ssId);
    var sheet = ss.getSheetByName('Characters') || ss.getSheets()[0];

    var lastRow = sheet.getLastRow();
    var newId = lastRow;

    var now = new Date();

    // ステータスを空（または0）で登録
    // Name が空、HP=0 の場合、Pythonアプリがこれを検出してAI生成を実行
    sheet.appendRow([
      newId,
      '',           // Name (空 - AI生成待ち)
      imageUrl,     // Image URL
      imageUrl,     // Sprite URL
      0,            // HP (0 - AI生成待ち)
      0,            // Attack (0 - AI生成待ち)
      0,            // Defense (0 - AI生成待ち)
      0,            // Speed (0 - AI生成待ち)
      0,            // Magic (0 - AI生成待ち)
      '',           // Description (空 - AI生成待ち)
      now,          // Created At
      0,            // Wins
      0,            // Losses
      0             // Draws
    ]);

    return ContentService.createTextOutput(JSON.stringify({
      ok: true,
      message: 'Character registered successfully (stats will be generated by AI on app startup)',
      characterId: newId,
      imageUrl: imageUrl
    })).setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({
      ok: false,
      error: err.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

