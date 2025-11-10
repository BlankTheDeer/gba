#!/bin/bash
# ============================================
# BlankTB Portal Backend Startup Script
# --------------------------------------------
# 🦌 Automatically starts the FastAPI backend
# using the local venv and environment vars.
# ============================================

cd "$(dirname "$0")" || exit 1

# Activate virtual environment
if [ -d ".venv" ]; then
  source .venv/bin/activate
else
  echo "⚠️ No virtual environment found. Creating one..."
  python3 -m venv .venv
  source .venv/bin/activate
  pip install --upgrade pip
  if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
  else
    pip install fastapi uvicorn motor aiohttp python-dotenv psutil
  fi
fi

echo "🚀 Launching BlankTB Portal Backend..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${SERVER_PORT:-8000}" --reload
