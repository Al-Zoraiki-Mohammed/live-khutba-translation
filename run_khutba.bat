@echo off
cd /d %~dp0
echo ========================================
echo Starting Khutba Translation App via uv...
echo ========================================

:: 1. Launch the Python backend in the background via uv
start /b uv run python backend/app.py

:: 2. Wait 3 seconds for the WebSocket server to boot
timeout /t 3 >nul

:: 3. Open index.html in whatever DEFAULT browser Windows is set to use
start "" "%~dp0frontend\index.html"

:: 4. Keep running for 45 minutes (2700 seconds)
echo Khutba app is running. It will auto-close in 45 minutes...
timeout /t 2700

:: 5. Safely stop the backend process when time is up
taskkill /f /im python.exe
echo Khutba session completed. Exiting...
exit
