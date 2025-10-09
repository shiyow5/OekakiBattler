require('dotenv').config();
const express = require('express');
const line = require('@line/bot-sdk');
const axios = require('axios');
const sharp = require('sharp');

const app = express();
const config = {
  channelAccessToken: process.env.LINE_CHANNEL_ACCESS_TOKEN,
  channelSecret: process.env.LINE_CHANNEL_SECRET,
};
const client = new line.Client(config);

// セッション管理用（本番環境ではRedisやDBを使用することを推奨）
const userSessions = new Map();

// セッション状態の定義
const SESSION_STATE = {
  WAITING_FOR_IMAGE: 'waiting_for_image',
  ASKING_MANUAL_INPUT: 'asking_manual_input',
  WAITING_FOR_NAME: 'waiting_for_name',
  WAITING_FOR_HP: 'waiting_for_hp',
  WAITING_FOR_ATTACK: 'waiting_for_attack',
  WAITING_FOR_DEFENSE: 'waiting_for_defense',
  WAITING_FOR_SPEED: 'waiting_for_speed',
  WAITING_FOR_MAGIC: 'waiting_for_magic',
  WAITING_FOR_LUCK: 'waiting_for_luck',
  WAITING_FOR_DESCRIPTION: 'waiting_for_description',
};

// セッションの初期化
function initSession(userId) {
  return {
    state: SESSION_STATE.WAITING_FOR_IMAGE,
    imageUrl: null,
    fileId: null,
    manualInput: false,
    characterData: {
      name: null,
      hp: null,
      attack: null,
      defense: null,
      speed: null,
      magic: null,
      luck: null,
      description: null,
    },
  };
}

// セッションの取得または作成
function getSession(userId) {
  if (!userSessions.has(userId)) {
    userSessions.set(userId, initSession(userId));
  }
  return userSessions.get(userId);
}

// セッションのクリア
function clearSession(userId) {
  userSessions.delete(userId);
}

// LINEメッセージを送信するヘルパー関数
async function replyMessage(replyToken, messages) {
  return client.replyMessage(replyToken, messages);
}

// LINE ミドルウェアで署名検証と body パースを行う
app.post('/webhook', line.middleware(config), async (req, res) => {
  try {
    const events = req.body.events || [];
    for (const event of events) {
      await handleEvent(event);
    }
    res.status(200).send('OK');
  } catch (err) {
    console.error(err);
    res.status(500).send('error');
  }
});

async function handleEvent(event) {
  const userId = event.source.userId;
  const session = getSession(userId);

  // 画像メッセージの処理
  if (event.type === 'message' && event.message.type === 'image') {
    const messageId = event.message.id;

    // LINE のコンテンツ取得 API を直接呼んでバイナリを得る
    const url = `https://api-data.line.me/v2/bot/message/${messageId}/content`;
    const resp = await axios.get(url, {
      responseType: 'arraybuffer',
      headers: { Authorization: `Bearer ${process.env.LINE_CHANNEL_ACCESS_TOKEN}` },
    });
    let buffer = Buffer.from(resp.data);
    const contentType = resp.headers['content-type'] || 'image/jpeg';
    const ext = contentType.split('/')[1] || 'jpg';
    const isPng = contentType === 'image/png' || ext === 'png';

    let finalMimeType = contentType;
    let finalFilename = `line_${messageId}.${ext}`;

    // 画像を圧縮してサイズを削減（最大1024px）
    // PNG形式の場合は透過情報を保持
    try {
      const sharpImage = sharp(buffer)
        .resize(1024, 1024, {
          fit: 'inside',
          withoutEnlargement: true
        });

      if (isPng) {
        // PNG形式: 透過情報を保持して圧縮
        buffer = await sharpImage
          .png({ quality: 80, compressionLevel: 8 })
          .toBuffer();
        finalMimeType = 'image/png';
        finalFilename = `line_${messageId}.png`;
      } else {
        // JPEG形式: JPEG品質80%で圧縮
        buffer = await sharpImage
          .jpeg({ quality: 80 })
          .toBuffer();
        finalMimeType = 'image/jpeg';
        finalFilename = `line_${messageId}.jpg`;
      }

      console.log(`Image compressed to ${buffer.length} bytes (${finalMimeType})`);
    } catch (compressError) {
      console.warn('Image compression failed, using original:', compressError);
    }

    // GAS に画像を送る（Base64 + mime + filename + secret + source）
    const gasResponse = await axios.post(process.env.GAS_WEBHOOK_URL, {
      image: buffer.toString('base64'),
      mimeType: finalMimeType,
      filename: finalFilename,
      secret: process.env.SHARED_SECRET,
      source: 'linebot',
      action: 'upload',
    }, { timeout: 60000 });  // タイムアウトを60秒に延長

    if (gasResponse.data && gasResponse.data.ok) {
      session.imageUrl = gasResponse.data.url;
      session.fileId = gasResponse.data.fileId;
      session.state = SESSION_STATE.ASKING_MANUAL_INPUT;

      // ステータス入力方法を尋ねる
      await replyMessage(event.replyToken, [
        {
          type: 'text',
          text: '画像を受け取りました！\nステータス入力方法の選択に移ります。',
        },
        {
          type: 'template',
          altText: 'ステータス入力方法を選択してください',
          template: {
            type: 'buttons',
            text: 'キャラクターのステータスを手動で入力しますか？',
            actions: [
              {
                type: 'message',
                label: 'はい（手動入力）',
                text: 'はい',
              },
              {
                type: 'message',
                label: 'いいえ（AI自動生成）',
                text: 'いいえ',
              },
            ],
          },
        },
      ]);
    } else {
      await replyMessage(event.replyToken, {
        type: 'text',
        text: '画像のアップロードに失敗しました。もう一度お試しください。',
      });
      clearSession(userId);
    }
    return;
  }

  // テキストメッセージの処理
  if (event.type === 'message' && event.message.type === 'text') {
    const text = event.message.text.trim();

    // ステータス入力方法の回答を処理
    if (session.state === SESSION_STATE.ASKING_MANUAL_INPUT) {
      if (text === 'はい') {
        session.manualInput = true;
        session.state = SESSION_STATE.WAITING_FOR_NAME;
        await replyMessage(event.replyToken, {
          type: 'text',
          text: 'キャラクター名を入力してください：',
        });
      } else if (text === 'いいえ') {
        session.manualInput = false;
        // AI自動生成でキャラクター登録
        await registerCharacterAuto(event.replyToken, session);
        clearSession(userId);
      } else {
        await replyMessage(event.replyToken, {
          type: 'text',
          text: '「はい」または「いいえ」で答えてください。',
        });
      }
      return;
    }

    // 手動入力フロー
    if (session.manualInput) {
      switch (session.state) {
        case SESSION_STATE.WAITING_FOR_NAME:
          session.characterData.name = text;
          session.state = SESSION_STATE.WAITING_FOR_HP;
          await replyMessage(event.replyToken, {
            type: 'text',
            text: '各ステータスの入力に移ります。\n※ステータス合計は350までにしてください。\n\nまず、HP（10-200）を入力してください：',
          });
          break;

        case SESSION_STATE.WAITING_FOR_HP:
          const hp = parseInt(text);
          if (isNaN(hp) || hp < 10 || hp > 200) {
            await replyMessage(event.replyToken, {
              type: 'text',
              text: 'HPは10〜200の数値で入力してください。',
            });
          } else {
            session.characterData.hp = hp;
            session.state = SESSION_STATE.WAITING_FOR_ATTACK;
            await replyMessage(event.replyToken, {
              type: 'text',
              text: '攻撃力（10-150）を入力してください：',
            });
          }
          break;

        case SESSION_STATE.WAITING_FOR_ATTACK:
          const attack = parseInt(text);
          if (isNaN(attack) || attack < 10 || attack > 150) {
            await replyMessage(event.replyToken, {
              type: 'text',
              text: '攻撃力は10〜150の数値で入力してください。',
            });
          } else {
            session.characterData.attack = attack;
            session.state = SESSION_STATE.WAITING_FOR_DEFENSE;
            await replyMessage(event.replyToken, {
              type: 'text',
              text: '防御力（10-100）を入力してください：',
            });
          }
          break;

        case SESSION_STATE.WAITING_FOR_DEFENSE:
          const defense = parseInt(text);
          if (isNaN(defense) || defense < 10 || defense > 100) {
            await replyMessage(event.replyToken, {
              type: 'text',
              text: '防御力は10〜100の数値で入力してください。',
            });
          } else {
            session.characterData.defense = defense;
            session.state = SESSION_STATE.WAITING_FOR_SPEED;
            await replyMessage(event.replyToken, {
              type: 'text',
              text: '素早さ（10-100）を入力してください：',
            });
          }
          break;

        case SESSION_STATE.WAITING_FOR_SPEED:
          const speed = parseInt(text);
          if (isNaN(speed) || speed < 10 || speed > 100) {
            await replyMessage(event.replyToken, {
              type: 'text',
              text: '素早さは10〜100の数値で入力してください。',
            });
          } else {
            session.characterData.speed = speed;
            session.state = SESSION_STATE.WAITING_FOR_MAGIC;
            await replyMessage(event.replyToken, {
              type: 'text',
              text: '魔力（10-100）を入力してください：',
            });
          }
          break;

        case SESSION_STATE.WAITING_FOR_MAGIC:
          const magic = parseInt(text);
          if (isNaN(magic) || magic < 10 || magic > 100) {
            await replyMessage(event.replyToken, {
              type: 'text',
              text: '魔力は10〜100の数値で入力してください。',
            });
          } else {
            session.characterData.magic = magic;
            session.state = SESSION_STATE.WAITING_FOR_LUCK;
            await replyMessage(event.replyToken, {
              type: 'text',
              text: '運（0-100）を入力してください：',
            });
          }
          break;

        case SESSION_STATE.WAITING_FOR_LUCK:
          const luck = parseInt(text);
          if (isNaN(luck) || luck < 0 || luck > 100) {
            await replyMessage(event.replyToken, {
              type: 'text',
              text: '運は0〜100の数値で入力してください。',
            });
          } else {
            session.characterData.luck = luck;

            // Check total stats limit (350)
            const totalStats = session.characterData.hp + session.characterData.attack +
                              session.characterData.defense + session.characterData.speed +
                              session.characterData.magic + session.characterData.luck;

            if (totalStats > 350) {
              await replyMessage(event.replyToken, {
                type: 'text',
                text: `ステータス合計が350を超えています（合計: ${totalStats}）。\n\n各ステータスを調整してください。最初からやり直すには画像を再送信してください。`,
              });
              clearSession(userId);
            } else {
              session.state = SESSION_STATE.WAITING_FOR_DESCRIPTION;
              await replyMessage(event.replyToken, {
                type: 'text',
                text: 'キャラクターの説明を入力してください：',
              });
            }
          }
          break;

        case SESSION_STATE.WAITING_FOR_DESCRIPTION:
          session.characterData.description = text;
          // 手動入力でキャラクター登録
          await registerCharacterManual(event.replyToken, session);
          clearSession(userId);
          break;

        default:
          await replyMessage(event.replyToken, {
            type: 'text',
            text: '画像を送信してキャラクター登録を開始してください。',
          });
          break;
      }
    }
  }
}

// AI自動生成でキャラクター登録（ステータスは空で登録、Python側で生成）
async function registerCharacterAuto(replyToken, session) {
  try {
    // GASにリクエストを送信（ステータスは空で登録）
    const response = await axios.post(process.env.GAS_WEBHOOK_URL, {
      action: 'register_character_auto',
      secret: process.env.SHARED_SECRET,
      imageUrl: session.imageUrl,
      fileId: session.fileId,
    }, { timeout: 30000 });

    if (response.data && response.data.ok) {
      await replyMessage(replyToken, {
        type: 'text',
        text: `画像を登録しました！\n\nキャラクターのステータスは、お絵描きバトラーアプリを起動したときにAIが自動生成します。\n\nアプリを開いて確認してください！`,
      });
    } else {
      await replyMessage(replyToken, {
        type: 'text',
        text: 'キャラクター登録に失敗しました。',
      });
    }
  } catch (error) {
    console.error('Auto registration error:', error);
    await replyMessage(replyToken, {
      type: 'text',
      text: 'キャラクター登録中にエラーが発生しました。',
    });
  }
}

// 手動入力でキャラクター登録
async function registerCharacterManual(replyToken, session) {
  try {
    // GASに手動入力データを送信
    const response = await axios.post(process.env.GAS_WEBHOOK_URL, {
      action: 'register_character_manual',
      secret: process.env.SHARED_SECRET,
      imageUrl: session.imageUrl,
      fileId: session.fileId,
      characterData: session.characterData,
    }, { timeout: 30000 });

    if (response.data && response.data.ok) {
      const char = session.characterData;
      const totalStats = char.hp + char.attack + char.defense + char.speed + char.magic + char.luck;
      await replyMessage(replyToken, {
        type: 'text',
        text: `キャラクター「${char.name}」を登録しました！\n\nステータス：\nHP: ${char.hp}\n攻撃: ${char.attack}\n防御: ${char.defense}\n素早さ: ${char.speed}\n魔力: ${char.magic}\n運: ${char.luck}\n合計: ${totalStats}/350\n\n説明: ${char.description}`,
      });
    } else {
      await replyMessage(replyToken, {
        type: 'text',
        text: 'キャラクター登録に失敗しました。',
      });
    }
  } catch (error) {
    console.error('Manual registration error:', error);
    await replyMessage(replyToken, {
      type: 'text',
      text: 'キャラクター登録中にエラーが発生しました。',
    });
  }
}

const port = process.env.PORT || 3000;
app.listen(port, ()=> console.log(`listening on ${port}`));
