#!/bin/bash
# 🦌 BlankTB Portal Backend Launcher
cd /home/container

echo "🌸 Starting BlankTB Portal Backend..."
echo "🦌 Running on port ${SERVER_PORT}"

# Load environment
export $(grep -v '^#' .env | xargs)

# Start backend
uvicorn app.main:app --host 0.0.0.0 --port ${SERVER_PORT}
