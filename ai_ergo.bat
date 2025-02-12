@echo off

start call "C:\1backup zano 2\TMMIN\AI Ergonomic\ai_backend.bat"; timeout /t 30 /nobreak
start call "C:\1backup zano 2\TMMIN\AI Ergonomic\ai_frontend.bat"
sleep 20
start chrome http://localhost:3000/img