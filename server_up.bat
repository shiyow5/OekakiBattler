@echo off
REM Windows batch script to start LINE Bot server with ngrok

echo Starting LINE Bot server...

cd server
call npm install express @line/bot-sdk axios dotenv sharp

echo Starting Node.js server...
start "LINEBOT_NODE" /B node server.js
set NODE_PID=%ERRORLEVEL%

echo Starting ngrok tunnel...
echo Note: If ngrok is not configured, run: ngrok config add-authtoken YOUR_AUTHTOKEN
echo Get your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken

REM ngrok をフォアグラウンドで実行
ngrok http 3000

REM ngrok が終了したら Node も終了させる
echo Stopping Node.js server...
taskkill /F /IM node.exe >nul 2>&1
