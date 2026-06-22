@echo off
echo ====================================================
echo Setting up Python Virtual Environment and Backend Dependencies...
echo ====================================================

cd backend

:: Check if virtual environment already exists, if not, create it
if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
)

:: Activate the virtual environment and install core AI packages
echo Activating virtual environment...
call venv\Scripts\activate

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing backend dependencies...
:: Core packages: fastapi (API), uvicorn (server), pinecone-client, openai, pandas (ETL), python-dotenv
pip install fastapi uvicorn pinecone openai pandas pydantic python-dotenv

:: Freeze dependencies to requirements.txt for tracking
pip freeze > requirements.txt

echo ====================================================
echo Backend environment setup complete! Virtual environment is ready.
echo ====================================================
pause