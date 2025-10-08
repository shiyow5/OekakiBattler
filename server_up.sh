#!/usr/bin/bash

cd server/
npm install express @line/bot-sdk axios dotenv sharp

node server.js &
NODE_PID=$!

ngrok http 3000
NGROK_PID=$!

# Ctrl+C や kill 時に両方止める
trap "echo 'Stopping...'; kill $NODE_PID $NGROK_PID; exit" INT TERM

# wait で ngrok が終了するまで待機
wait $NGROK_PID

# ngrokの初期設定(https://dashboard.ngrok.com/get-started/your-authtoken)
# ngrok config add-authtoken <YOUR_AUTHTOKEN>
