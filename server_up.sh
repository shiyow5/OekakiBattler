#!/usr/bin/bash

cd server/
npm install express @line/bot-sdk axios dotenv sharp

node server.js &
NODE_PID=$!

# Ctrl+C(SIGINT) や終了(SIGTERM)時に node を殺す
trap "echo 'Stopping...'; kill $NODE_PID; exit" INT TERM

ngrok http 3000

# ngrokの初期設定(https://dashboard.ngrok.com/get-started/your-authtoken)
# ngrok config add-authtoken <YOUR_AUTHTOKEN>
