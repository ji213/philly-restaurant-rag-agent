@echo off
:: Navigate to backend, open PowerShell, activate venv, and execute pipeline
powershell -NoExit -ExecutionPolicy Bypass -Command "cd backend; .\venv\Scripts\Activate.ps1; python scripts/import_yelpreviewdata.py"