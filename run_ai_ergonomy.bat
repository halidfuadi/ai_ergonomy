@echo off
echo Menjalankan AI Ergonomy...

:: Jalankan Backend
start cmd /k "cd backend && call venv\Scripts\activate && python main_live.py"

:: Tunggu beberapa detik agar backend siap
timeout /t 5 /nobreak

:: Jalankan Frontend
start cmd /k "cd frontend && npm run dev"

echo Sistem berjalan! Backend dan Frontend telah dimulai.
pause
