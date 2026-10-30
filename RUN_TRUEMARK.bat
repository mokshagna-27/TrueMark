@echo off
setlocal
title TrueMark - Startup
cd /d "%~dp0"

echo.
echo ==========================================
echo        TrueMark - Application Launcher
echo ==========================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python was not found. Install Python 3.11 or newer and enable "Add Python to PATH".
    pause
    exit /b 1
)

where node >nul 2>nul
if errorlevel 1 (
    echo ERROR: Node.js was not found. Install Node.js 22 LTS, then reopen this file.
    pause
    exit /b 1
)

where npm >nul 2>nul
if errorlevel 1 (
    echo ERROR: npm was not found. Reinstall Node.js and ensure npm is added to PATH.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo [1/4] Creating Python virtual environment...
    python -m venv .venv
    if errorlevel 1 goto :error
)

echo [2/4] Installing backend dependencies...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :error
".venv\Scripts\python.exe" -m pip install -r "backend\requirements.txt"
if errorlevel 1 goto :error

echo [3/4] Installing frontend dependencies (first run may take a few minutes)...
pushd "frontend"
call npm ci
if errorlevel 1 (
    popd
    echo npm ci failed. Check your internet connection and package-lock.json.
    goto :error
)
popd

echo [4/4] Starting backend and frontend...
start "TrueMark Backend - FastAPI" cmd /k "cd /d ""%~dp0backend"" && ""%~dp0.venv\Scripts\python.exe"" -m uvicorn main:app --reload --host 127.0.0.1 --port 8000"
timeout /t 3 /nobreak >nul
start "TrueMark Frontend - Vite" cmd /k "cd /d ""%~dp0frontend"" && npm run dev -- --host 127.0.0.1"
echo.
echo TrueMark is starting.
echo Frontend: http://127.0.0.1:5173
echo Backend API docs: http://127.0.0.1:8000/docs
echo Keep both terminal windows open while using the app.
echo.
pause
exit /b 0

:error
echo.
echo Startup did not complete. Read the error above, fix the listed dependency or setup issue, and run this file again.
pause
exit /b 1
