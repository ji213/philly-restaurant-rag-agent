@echo off
echo Starting FastAPI Backend Pipeline...

cd /d "%~dp0"

if not exist "venv" (
    echo Creating virtual environment 'venv'...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing / verifying dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo Starting Uvicorn server...
uvicorn main:app --reload
pause