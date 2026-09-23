@echo off
echo ===================================================
echo Starting SupportPilot Full Stack Application Services
echo ===================================================

:: 1. Start Knowledge Base API on Port 8001 (Classification API)
echo Launching Knowledge Base API on Port 8001...
start "SupportPilot - KB API (Port 8001)" cmd /k "cd /d %~dp0supportpilot-api_new_fast\supportpilot-api && %~dp0rag_module\venv\Scripts\python.exe -m uvicorn app.main:app --port 8001 --host 127.0.0.1"

:: Small delay to let KB API initialize first
timeout /t 3 /nobreak >nul

:: 2. Start RAG Backend on Port 8000
echo Launching RAG Backend on Port 8000...
start "SupportPilot - RAG Backend (Port 8000)" cmd /k "cd /d %~dp0rag_module && venv\Scripts\python.exe -m uvicorn app.main:app --port 8000 --host 127.0.0.1"

:: Small delay to let backend initialize
timeout /t 3 /nobreak >nul

:: 3. Start React Frontend
echo Launching Vite React Frontend...
start "SupportPilot - React Frontend" cmd /k "cd /d %~dp0ticket-app && npm run dev"

echo ===================================================
echo All services are starting up in separate windows.
echo - Frontend:           http://localhost:5173
echo - RAG API Backend:    http://localhost:8000
echo - KB API Backend:     http://localhost:8001
echo ===================================================
echo.
echo Wait 20-30 seconds for all services to fully start,
echo then open http://localhost:5173 in your browser.
echo ===================================================
pause
