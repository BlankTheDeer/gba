#!/usr/bin/env python3
# 🦌 BlankTB Portal — External Healthcheck Script
# Pings backend endpoints and sends Discord alerts if they fail.
# Intended to be run by systemd timer.
# (c) BlankTB — All Rights Reserved

import os
import json
import datetime
import sys
from pathlib import Path

import requests

# 🧭 Config (override via env if you want)
BASE_URL = os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8000")
STATUS_URL = f"{BASE_URL}/api/status/public"
DEBUG_URL = f"{BASE_URL}/api/debug/ui"

DISCORD_WEBHOOK = os.getenv("DISCORD_HEALTHCHECK_WEBHOOK", "")  # <--- set in .env
TIMEOUT_SECONDS = int(os.getenv("HEALTHCHECK_TIMEOUT", "5"))
FAIL_THRESHOLD = int(os.getenv("HEALTHCHECK_FAIL_THRESHOLD", "1"))  # consecutive fails

# State file to avoid spamming Discord
STATE_FILE = Path("/home/blankthedeer/gba/backend/health_state.json")


def load_state():
    if not STATE_FILE.exists():
        return {"overall_status": "unknown", "consecutive_failures": 0, "last_message": ""}
    try:
        with STATE_FILE.open("r") as f:
            return json.load(f)
    except Exception:
        return {"overall_status": "unknown", "consecutive_failures": 0, "last_message": ""}


def save_state(state: dict):
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with STATE_FILE.open("w") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"[healthcheck] Failed to write state file: {e}", file=sys.stderr)


def send_discord_message(title: str, description: str, color: int = 0xE74C3C):
    """Send a simple embed to Discord webhook."""
    if not DISCORD_WEBHOOK:
        print("[healthcheck] No DISCORD_HEALTHCHECK_WEBHOOK set, skipping alert.")
        return

    payload = {
        "embeds": [{
            "title": title,
            "description": description,
            "color": color,
            "footer": {"text": "BlankTB Portal Healthcheck 🦌"},
            "timestamp": datetime.datetime.utcnow().isoformat()
        }]
    }

    try:
        resp = requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
        if resp.status_code >= 400:
            print(f"[healthcheck] Discord webhook error: {resp.status_code} {resp.text}", file=sys.stderr)
    except Exception as e:
        print(f"[healthcheck] Failed to send Discord alert: {e}", file=sys.stderr)


def main():
    state = load_state()
    now = datetime.datetime.utcnow().isoformat()
    failures = []

    # Check /api/status/public
    try:
        r = requests.get(STATUS_URL, timeout=TIMEOUT_SECONDS)
        if not (200 <= r.status_code < 300):
            failures.append(f"/api/status/public → HTTP {r.status_code}")
    except Exception as e:
        failures.append(f"/api/status/public → error: {e}")

    # Check /api/debug/ui
    try:
        r2 = requests.get(DEBUG_URL, timeout=TIMEOUT_SECONDS)
        if not (200 <= r2.status_code < 300):
            failures.append(f"/api/debug/ui → HTTP {r2.status_code}")
    except Exception as e:
        failures.append(f"/api/debug/ui → error: {e}")

    if failures:
        # Something is wrong
        state["consecutive_failures"] = state.get("consecutive_failures", 0) + 1
        state["overall_status"] = "failed"

        print(f"[healthcheck] FAIL at {now}: {failures}")

        if state["consecutive_failures"] >= FAIL_THRESHOLD:
            # Only send alert if state changed or we just crossed threshold
            msg = "\n".join(failures)
            summary = f"🔴 BlankTB Backend Healthcheck FAILED"
            desc = f"Time (UTC): `{now}`\nBase URL: `{BASE_URL}`\n\nIssues:\n{msg}"

            # Avoid spamming exact same message repeatedly
            last_message = state.get("last_message", "")
            if msg != last_message:
                send_discord_message(summary, desc, color=0xE74C3C)
                state["last_message"] = msg
    else:
        # All good
        if state.get("overall_status") == "failed":
            # Recovery message
            summary = "🟢 BlankTB Backend Recovered"
            desc = f"Time (UTC): `{now}`\nBase URL: `{BASE_URL}`\n\nAll monitored endpoints responded successfully."
            send_discord_message(summary, desc, color=0x2ECC71)

        print(f"[healthcheck] OK at {now}")
        state["overall_status"] = "ok"
        state["consecutive_failures"] = 0
        state["last_message"] = ""

    save_state(state)


if __name__ == "__main__":
    main()
