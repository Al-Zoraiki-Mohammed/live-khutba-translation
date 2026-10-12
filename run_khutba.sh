#!/bin/bash

# Navigate to the project directory
cd "$(dirname "$0")"

echo "========================================"
echo "Starting Khutba Translation App via uv..."
echo "========================================"

# Run backend using uv directly in the background
uv run python backend/app.py &
BACKEND_PID=$!

# Wait 3 seconds for the server to boot
sleep 3

# Open browser automatically (macOS 'open' or Linux 'xdg-open')
if [[ "$OSTYPE" == "darwin"* ]]; then
    open -a "Google Chrome" http://localhost:8765
else
    xdg-open http://localhost:8765
fi

# Sleep for 45 minutes (45 * 60 = 2700 seconds)
sleep 2700

# Kill the backend process and close Chrome
kill $BACKEND_PID
pkill -f "Google Chrome"
