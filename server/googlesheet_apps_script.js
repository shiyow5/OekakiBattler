// Google Apps Script (doPost)
function doPost(e) {
  try {
    if (!e.postData || !e.postData.contents) return ContentService.createTextOutput('no data');

    var payload = JSON.parse(e.postData.contents);

    // 簡易的なシークレット確認（Node側で送る secret を検査）
    var SHARED_SECRET = 'oekaki_battler_line_to_gas_secret_shiyow5'; // ← デプロイ前に合わせる
    if (!payload.secret || payload.secret !== SHARED_SECRET) {
      return ContentService.createTextOutput(JSON.stringify({ok:false, error:'forbidden'}))
             .setMimeType(ContentService.MimeType.JSON);
    }

    var b64 = payload.image;
    var mime = payload.mimeType || 'image/jpeg';
    var filename = payload.filename || ('line_' + new Date().getTime() + '.jpg');

    // Base64 をデコードして blob を作成
    var blob = Utilities.newBlob(Utilities.base64Decode(b64), mime, filename);

    // Drive に保存（フォルダIDを指定する場合は getFolderById）
    var folderId = '1JT7QnTcSrLo2AC4p580V7fa_MScuVd4G';
    var file;
    if (folderId) {
      var folder = DriveApp.getFolderById(folderId);
      file = folder.createFile(blob);
    } else {
      file = DriveApp.createFile(blob);
    }

    // 共有リンク（誰でも閲覧に設定）
    file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
    var url = file.getUrl();

    // スプレッドシートに追記
    var ssId = '1asfRGrWkPRszQl4IUDO20o9Z7cgnV1bEVKVNt6cmKfM';
    var ss = SpreadsheetApp.openById(ssId);
    var sheet = ss.getSheetByName('Sheet1') || ss.getSheets()[0];
    var now = new Date();
    sheet.appendRow([now, filename, url]);

    // 画像をシートに貼り付け（必要なら。※blobサイズ上限あり）
    var lastRow = sheet.getLastRow();
    try {
      // 列番号は例：4列目に挿入
      sheet.insertImage(file.getBlob(), 4, lastRow);
    } catch (err) {
      // 挿入できない（サイズ等）場合は無視しておく
      console.warn('insertImage failed:', err);
    }

    return ContentService.createTextOutput(JSON.stringify({ok:true, url:url}))
           .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ok:false, error:err.toString()}))
           .setMimeType(ContentService.MimeType.JSON);
  }
}
