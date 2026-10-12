@echo off
cd /d %~dp0
echo ========================================
echo Starting Khutba Translation App via uv...
echo ========================================

:: uv run automatically provisions/uses the environment and runs the backend
start /b uv run python backend/app.py

:: Wait 3 seconds for the server to spin up
timeout /t 3 >nul

:: Open Chrome in kiosk mode.
start chrome --kiosk http://localhost:8765

:: Set timer for 45 minutes (45 min * 60 sec = 2700 seconds)
echo Khutba app is running. It will auto-close in 45 minutes...
timeout /t 2700

:: Terminate processes when time is up
taskkill /f /im python.exe
taskkill /f /im chrome.exe
exit
