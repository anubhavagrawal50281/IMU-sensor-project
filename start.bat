@echo off
title Motion Studio
cd /d "%~dp0"

echo.
echo  ================================================
echo   Motion Studio  ^|  Local Dashboard
echo  ================================================
echo.

REM ── Check Python ─────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python not found.
    echo  Install Python 3.11 from https://python.org
    pause
    exit /b 1
)

REM ── Create venv if missing ────────────────────────
if not exist "venv\Scripts\python.exe" (
    echo  First run — setting up virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo  ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo  Installing dependencies...
    venv\Scripts\pip install -r localhost\requirements.txt --quiet
    if errorlevel 1 (
        echo  ERROR: Failed to install dependencies.
        pause
        exit /b 1
    )
    echo  Setup complete!
    echo.
) else (
    echo  Virtual environment found.
)

REM ── Start server in new window ────────────────────
echo  Starting server...
start "Motion Studio — Server" cmd /k "cd /d %~dp0localhost && ..\venv\Scripts\python.exe main.py"

REM ── Wait for server to boot ───────────────────────
echo  Waiting for server to start...
timeout /t 4 /nobreak >nul

REM ── Open Chrome ──────────────────────────────────
echo  Opening Chrome...

REM Try Chrome in PATH first
where chrome >nul 2>&1
if not errorlevel 1 (
    start "" chrome "http://localhost:8000"
    goto done
)

REM Try common Chrome install locations
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" "http://localhost:8000"
    goto done
)
if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    start "" "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" "http://localhost:8000"
    goto done
)
if exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" (
    start "" "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" "http://localhost:8000"
    goto done
)

REM Fallback to default browser
start "" "http://localhost:8000"

:done
echo.
echo  ================================================
echo   Running at  http://localhost:8000
echo   Phone URL   shown in the server window
echo   Close the server window to stop.
echo  ================================================
echo.
