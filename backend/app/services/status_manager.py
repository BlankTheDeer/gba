#!/usr/bin/env python3
# 🦌 BlankTB Portal — Status Manager Service
# Tracks uptime, service status, and historical trends.
# Includes caching, Discord webhook alerting, and health summaries.
# (c) BlankTB — All Rights Reserved

import datetime
import asyncio
import json
import os
import aiohttp
from app.core.config import mongo_db
from app.services import status_helper

# Mongo Collection
COLLECTION_NAME = "status_history"

# Settings
RETENTION_DAYS = 30
LOG_INTERVAL_MINUTES = 10
CACHE_FILE = "/home/blankthedeer/gba/backend/status_cache.json"
CACHE_TTL_MINUTES = 10
ALERT_STATE_FILE = "/home/blankthedeer/gba/backend/status_alerts.json"

# Discord Webhooks
DISCORD_ALERT_WEBHOOK = os.getenv("DISCORD_ALERT_WEBHOOK", "")
DISCORD_UPTIME_WEBHOOK = os.getenv("DISCORD_UPTIME_WEBHOOK", "")

# Service icons for a cute touch ✨
SERVICE_ICONS = {
    "website": "🦌",
    "user_login": "🔐",
    "api_gateway": "🌐",
    "storage": "💾",
    "support_portal": "💌"
}

# 🗂 Cache Handling
def _load_cache():
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, "r") as f:
            data = json.load(f)
        last_update = datetime.datetime.fromisoformat(data.get("last_updated"))
        age_minutes = (datetime.datetime.utcnow() - last_update).total_seconds() / 60
        if age_minutes > CACHE_TTL_MINUTES:
            return None
        return data
    except Exception:
        return None


def _save_cache(data: dict):
    try:
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, "w") as f:
            json.dump(data, f, indent=2, default=str)
    except Exception as e:
        print(f"[StatusManager] Cache write failed: {e}")


# 🧠 Alert State
def _load_alert_state():
    if not os.path.exists(ALERT_STATE_FILE):
        return {}
    try:
        with open(ALERT_STATE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_alert_state(data: dict):
    try:
        os.makedirs(os.path.dirname(ALERT_STATE_FILE), exist_ok=True)
        with open(ALERT_STATE_FILE, "w") as f:
            json.dump(data, f, indent=2, default=str)
    except Exception as e:
        print(f"[StatusManager] Alert state write failed: {e}")


# 🔔 Discord Alerts
async def send_discord_alert(service_changes: dict):
    """Send a grouped alert to Discord for multiple service updates."""
    if not DISCORD_ALERT_WEBHOOK:
        print(f"[Alert] No Discord webhook configured for alerts.")
        return

    try:
        fields = []
        for service, status in service_changes.items():
            emoji = "🔴" if status == "offline" else "🟡" if status == "maintenance" else "🟢"
            icon = SERVICE_ICONS.get(service, "💠")
            fields.append({
                "name": f"{emoji} {icon} {service.replace('_', ' ').title()}",
                "value": f"**{status.title()}**",
                "inline": True
            })

        embed = {
            "title": "🦌 Service Status Update",
            "description": f"{len(service_changes)} service(s) changed status.",
            "color": 0xF39C12,
            "fields": fields,
            "footer": {"text": "BlankTB Portal Backend Monitor 🦌"},
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

        async with aiohttp.ClientSession() as session:
            await session.post(DISCORD_ALERT_WEBHOOK, json={"embeds": [embed]})
        print(f"[Alert] Grouped Discord alert sent for {len(service_changes)} changes.")
    except Exception as e:
        print(f"[Alert Error] Failed to send Discord alert: {e}")


async def send_uptime_summary(uptime_data: dict):
    """Send weekly uptime summary to Discord."""
    if not DISCORD_UPTIME_WEBHOOK:
        return
    try:
        fields = []
        for service, pct in uptime_data["uptime"].items():
            color_emoji = "🟢" if pct >= 99 else "🟡" if pct >= 90 else "🔴"
            icon = SERVICE_ICONS.get(service, "💠")
            fields.append({
                "name": f"{color_emoji} {icon} {service.title()}",
                "value": f"**{pct}% uptime (7d)**",
                "inline": True
            })

        payload = {
            "embeds": [{
                "title": "📊 Weekly Uptime Report",
                "description": f"Service uptime over the last **{uptime_data['days']} days**",
                "color": 0x3498DB,
                "fields": fields,
                "footer": {"text": "BlankTB Portal Monitor 🦌"},
                "timestamp": datetime.datetime.utcnow().isoformat()
            }]
        }

        async with aiohttp.ClientSession() as session:
            await session.post(DISCORD_UPTIME_WEBHOOK, json=payload)
        print("[Alert] Uptime summary sent to Discord.")
    except Exception as e:
        print(f"[Alert Error] Could not send uptime summary: {e}")


# 🟢 Status Logger
async def log_current_status():
    """Fetch and store live service status."""
    try:
        services = {
            "website": "https://blanktb.net",
            "user_login": "http://localhost:8000/api/auth/ping",
            "api_gateway": "http://localhost:8000/",
            "storage": "http://localhost:8000/api/files/ping",
            "support_portal": "http://localhost:8000/api/help/ping",
        }

        results = await asyncio.gather(
            *[status_helper.check_service(url) for url in services.values()],
            return_exceptions=True
        )

        timestamp = datetime.datetime.utcnow()
        snapshot = {
            name: (
                "operational" if res == "operational"
                else "maintenance" if res == "degraded"
                else "offline"
            )
            for name, res in zip(services.keys(), results)
        }
        snapshot["last_updated"] = timestamp.isoformat()

        if mongo_db is not None:
            bulk_docs = [
                {"timestamp": timestamp, "service": name, "status": snapshot[name]}
                for name in services.keys()
            ]
            await mongo_db[COLLECTION_NAME].insert_many(bulk_docs)
        else:
            print("[StatusManager] Mongo not ready yet, skipping DB insert.")

        _save_cache(snapshot)
        await purge_old_records()
        await check_for_alerts(snapshot, timestamp)

        # Every hour, send uptime summary
        if timestamp.minute % 60 < LOG_INTERVAL_MINUTES:
            uptime_data = await calculate_uptime(7)
            await send_uptime_summary(uptime_data)

        return {"status": "ok", "count": len(services)}

    except Exception as e:
        print(f"[StatusManager] log_current_status failed: {e}")
        return {"status": "error", "detail": str(e)}


# 🚨 Alert Handling
async def check_for_alerts(snapshot: dict, timestamp: datetime.datetime):
    alert_state = _load_alert_state()
    updated = False
    changes = {}

    for service, status in snapshot.items():
        if service == "last_updated":
            continue
        prev = alert_state.get(service, {}).get("status")
        if prev != status:
            changes[service] = status
            alert_state[service] = {"status": status, "time": timestamp.isoformat()}
            updated = True

    if updated:
        _save_alert_state(alert_state)
        await send_discord_alert(changes)


# 🧹 Maintenance
async def purge_old_records():
    try:
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=RETENTION_DAYS)
        if mongo_db:
            await mongo_db[COLLECTION_NAME].delete_many({"timestamp": {"$lt": cutoff}})
    except Exception as e:
        print(f"[StatusManager] purge_old_records failed: {e}")


# 📊 Analytics
async def get_history(range_hours: int = 24):
    try:
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(hours=range_hours)
        cursor = mongo_db[COLLECTION_NAME].find({"timestamp": {"$gte": cutoff}})
        history = {}
        async for doc in cursor:
            s = doc["service"]
            history.setdefault(s, []).append({
                "timestamp": doc["timestamp"].isoformat(),
                "status": doc["status"]
            })
        return {"range_hours": range_hours, "services": history}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


async def calculate_uptime(days: int = 7):
    try:
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=days)
        cursor = mongo_db[COLLECTION_NAME].find({"timestamp": {"$gte": cutoff}})
        stats = {}
        async for doc in cursor:
            s = doc["service"]
            stats.setdefault(s, {"up": 0, "total": 0})
            stats[s]["total"] += 1
            if doc["status"] == "operational":
                stats[s]["up"] += 1
        uptime = {
            s: round((v["up"] / v["total"]) * 100, 2) if v["total"] > 0 else 0
            for s, v in stats.items()
        }
        return {"days": days, "uptime": uptime}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


# 💾 Cached Status + Summary
async def get_cached_status():
    data = _load_cache()
    if not data:
        print("[StatusManager] Cache expired or missing, refreshing...")
        await log_current_status()
        data = _load_cache()

    summary = []
    if data:
        for service, status in data.items():
            if service == "last_updated":
                continue
            emoji = "🟢" if status == "operational" else "🟡" if status == "maintenance" else "🔴"
            icon = SERVICE_ICONS.get(service, "💠")
            summary.append(f"{emoji} {icon} {service.replace('_', ' ').title()}: {status.title()}")

    return {
        "status": "ok",
        "last_updated": data.get("last_updated") if data else None,
        "summary": summary or ["No data available"],
        "raw": data
    }


# 📈 Detailed Status (for frontend graphs)
async def get_detailed_status(days: int = 7):
    """Returns uptime %, trend data, and summary for each service."""
    uptime_data = await calculate_uptime(days)
    history = await get_history(range_hours=days * 24)
    return {
        "uptime": uptime_data,
        "history": history,
        "generated_at": datetime.datetime.utcnow().isoformat()
    }


# ♻️ Auto Background Logger
async def auto_log_loop():
    await asyncio.sleep(10)
    print("[StatusManager] Background logger started 🦌")
    while True:
        result = await log_current_status()
        print(f"[StatusManager] Snapshot logged: {result}")
        await asyncio.sleep(LOG_INTERVAL_MINUTES * 60)
