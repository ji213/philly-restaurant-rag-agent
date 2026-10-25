@echo off
TITLE Philly Restaurant RAG Agent - Frontend
echo ====================================================
echo Starting Philly Restaurant Agent Frontend (Vite)
echo ====================================================

cd /d "%~dp0frontend"

:: Check if node_modules exists; if not, run npm install
if not exist "node_modules\" (
    echo [INFO] Installing frontend dependencies...
    call npm install
)

echo [INFO] Launching Vite development server...
call npm run dev

pause