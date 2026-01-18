#!/bin/bash

# Ensure we are in the backend directory or move there
if [ -d "backend" ]; then
    cd backend
fi

# Activate venv if it exists (optional check)
# source venv/bin/activate

# Install dependencies if needed (fast check)
echo "[INFO] Checking dependencies..."
python3 -m pip install -r requirements.txt

# Install playwright browsers if needed
echo "[INFO] Checking Playwright browsers..."
python3 -m playwright install

# Start the server
echo "[INFO] Starting Entropy Backend..."
# Make sure GOOGLE_API_KEY is set or read from .env
# We use python-dotenv in main.py, so it should be fine.
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
