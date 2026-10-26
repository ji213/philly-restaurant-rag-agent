@echo off
TITLE Philly Restaurant RAG Agent - Frontend Setup
echo ====================================================
echo Setting Up Philly Restaurant Agent Frontend
echo ====================================================

cd /d "%~dp0frontend"

echo [INFO] Installing main Node modules...
call npm install

echo [INFO] Installing required UI & styling packages...
call npm install lucide-react react-markdown

echo [INFO] Installing Tailwind CSS PostCSS plugin...
call npm install -D @tailwindcss/postcss

echo.
echo ====================================================
echo Frontend Setup Complete!
echo ====================================================
pause