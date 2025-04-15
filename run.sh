#!/bin/bash

# Activate virtual environment
source .venv/bin/activate

# Run Flask app in the background
python main.py &

# Save PID to kill later if needed
APP_PID=$!

# Wait a moment for the server to start
sleep 2

# Open default browser to localhost
xdg-open http://127.0.0.1:5001 2>/dev/null || open http://127.0.0.1:5001

# Wait for the Flask process to exit
wait $APP_PID