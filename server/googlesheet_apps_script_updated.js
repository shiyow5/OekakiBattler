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

    // LINE Bot用とPythonアプリ用の両方に対応
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
