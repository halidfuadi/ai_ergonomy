@echo off
echo Memulai instalasi dan menjalankan AI Ergonomy...

:: Backend setup
cd backend
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
start cmd /k "python main_live.py"
cd ..

:: Tunggu beberapa detik agar backend siap
timeout /t 5 /nobreak

:: Frontend setup
cd frontend
npm i
start cmd /k "npm run dev"
cd ..

echo Sistem siap digunakan!
pause
