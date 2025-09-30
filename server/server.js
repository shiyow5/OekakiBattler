require('dotenv').config();
const express = require('express');
const line = require('@line/bot-sdk');
const axios = require('axios');

const app = express();
const config = {
  channelAccessToken: process.env.LINE_CHANNEL_ACCESS_TOKEN,
  channelSecret: process.env.LINE_CHANNEL_SECRET,
};
const client = new line.Client(config);

// LINE ミドルウェアで署名検証と body パースを行う
app.post('/webhook', line.middleware(config), async (req, res) => {
  try {
    const events = req.body.events || [];
    for (const event of events) {
      if (event.type === 'message' && event.message.type === 'image') {
        const messageId = event.message.id;
        // LINE のコンテンツ取得 API を直接呼んでバイナリを得る
        const url = `https://api-data.line.me/v2/bot/message/${messageId}/content`;
        const resp = await axios.get(url, {
          responseType: 'arraybuffer',
          headers: { Authorization: `Bearer ${process.env.LINE_CHANNEL_ACCESS_TOKEN}` },
        });
        const buffer = Buffer.from(resp.data); // 画像のバイナリ
        const contentType = resp.headers['content-type'] || 'image/jpeg';
        const ext = contentType.split('/')[1] || 'jpg';
        const filename = `line_${messageId}.${ext}`;
        // GAS に送る（Base64 + mime + filename + secret）
        await axios.post(process.env.GAS_WEBHOOK_URL, {
          image: buffer.toString('base64'),
          mimeType: contentType,
          filename,
          secret: process.env.SHARED_SECRET
        }, { timeout: 10000 });
      }
    }
    res.status(200).send('OK');
  } catch (err) {
    console.error(err);
    res.status(500).send('error');
  }
});

const port = process.env.PORT || 3000;
app.listen(port, ()=> console.log(`listening on ${port}`));
