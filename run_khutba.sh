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

# Open frontend file using the system default browser
FRONTEND_PATH="$(pwd)/frontend/index.html"

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS: Opens file in the default browser
    open "$FRONTEND_PATH"
else
    # Linux: Opens file in the default desktop browser
    xdg-open "$FRONTEND_PATH"
fi

# Sleep for 45 minutes (45 * 60 = 2700 seconds)
sleep 2700

# Kill only the backend process safely (leaves user's browser tabs alone)
kill $BACKEND_PID
