#!/usr/bin/env python3
#  BlankTB Portal — Debug & Diagnostics API
# For internal use only — not exposed publicly
# (c) BlankTB — All Rights Reserved

import platform
import psutil
import datetime
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.core import config

router = APIRouter(prefix="/api/debug", tags=["Debug"])

@router.get("/ui", response_class=HTMLResponse)
async def debug_ui():
    """Displays system diagnostics, MongoDB status, and quick reconnect control."""
    try:
        db = config.mongo_db
        collections = await db.list_collection_names()
        db_status = '<span class="ok">Connected</span>'
    except Exception:
        collections = ["(DB not connected)"]
        db_status = '<span class="err">Disconnected</span>'

    uptime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sys_info = {
        "OS": platform.system(),
        "Release": platform.release(),
        "Python": platform.python_version(),
        "CPU": psutil.cpu_percent(),
        "RAM": round(psutil.virtual_memory().percent, 1)
    }

    html = f"""
    <html>
      <head>
        <title>BlankTB Portal — Backend Diagnostics</title>
        <link rel="icon" type="image/x-icon" href="/static/favicon.ico">
        <meta http-equiv="refresh" content="900"> <!-- Auto refresh every 15 minutes -->
        <style>
          body {{
            font-family: 'Inter', sans-serif;
            background: linear-gradient(120deg, #faf9ff, #e9e8f9);
            color: #333;
            padding: 2rem;
          }}
          h1 {{
            color: #7d2ae8;
            margin-bottom: 1.5rem;
          }}
          .card {{
            background: white;
            border-radius: 12px;
            padding: 1rem 1.5rem;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            margin-bottom: 1.5rem;
          }}
          ul {{ list-style: none; padding: 0; }}
          li {{ padding: 4px 0; }}
          .ok {{ color: #1ea463; font-weight: bold; }}
          .err {{ color: #e63946; font-weight: bold; }}
          .refresh-note {{
            font-size: 0.9rem;
            opacity: 0.7;
            margin-bottom: 0.5rem;
          }}
          .badge {{
            background: #7d2ae8;
            color: white;
            padding: 3px 8px;
            border-radius: 8px;
            font-size: 0.8rem;
          }}
          button {{
            background-color: #7d2ae8;
            color: white;
            border: none;
            padding: 8px 14px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
          }}
          button:hover {{
            background-color: #6a20d0;
          }}
        </style>
        <script>
          async function reconnectDB() {{
              const res = await fetch('/api/debug/reconnect');
              const data = await res.text();
              alert(data);
              location.reload();
          }}
        </script>
      </head>
      <body>
        <h1>BlankTB Portal Backend — Diagnostics</h1>
        <div class="refresh-note">Page refreshes automatically every 15 minutes </div>

        <div class="card">
          <h2>Server Status <span class="badge">LIVE</span></h2>
          <ul>
            <li>Status: <span class="ok">Running</span></li>
            <li>Uptime (approx.): {uptime}</li>
          </ul>
        </div>

        <div class="card">
          <h2>MongoDB Connection</h2>
          <ul>
            <li>Status: {db_status}</li>
            <li>Collections: {', '.join(collections)}</li>
          </ul>
          <button onclick="reconnectDB()">Reconnect Database</button>
        </div>

        <div class="card">
          <h2>System Information</h2>
          <ul>
            <li>OS: {sys_info['OS']} {sys_info['Release']}</li>
            <li>Python Version: {sys_info['Python']}</li>
            <li>CPU Usage: {sys_info['CPU']}%</li>
            <li>RAM Usage: {sys_info['RAM']}%</li>
          </ul>
        </div>

        <div class="card">
          <p>© BlankTB — Internal Diagnostics for development and verification only.<br>
          Backend powered by FastAPI • MongoDB • Uvicorn</p>
        </div>
      </body>
    </html>
    """
    return HTMLResponse(content=html)


@router.get("/reconnect", response_class=HTMLResponse)
async def reconnect_mongo():
    """Forces a reconnection attempt to MongoDB without restarting the backend."""
    try:
        await config.init_mongo()
        return HTMLResponse("✅ MongoDB reconnected successfully!")
    except Exception as e:
        return HTMLResponse(f"❌ Failed to reconnect: {e}")
