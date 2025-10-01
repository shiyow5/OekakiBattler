@echo off
REM Windows batch script to start LINE Bot server with ngrok

echo Starting LINE Bot server...

cd server
call npm install express @line/bot-sdk axios dotenv

echo Starting Node.js server...
start /B node server.js

echo Starting ngrok tunnel...
echo Note: If ngrok is not configured, run: ngrok config add-authtoken YOUR_AUTHTOKEN
echo Get your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken

ngrok http 3000

REM Note: When you close ngrok, you should also manually terminate the node process
REM You can find it with: tasklist | findstr node
REM And kill it with: taskkill /F /IM node.exe
