@echo off
cd /d "C:\Users\harro\OneDrive\Bureau\projects\api\pub-fast-api-v2"
call venv\Scripts\activate.bat
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
if %errorlevel% neq 0 pause

