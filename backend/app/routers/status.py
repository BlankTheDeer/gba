#!/usr/bin/env python3
# 🦌 BlankTB Portal — Status Router
# Handles public + internal system status endpoints for the BlankTB ecosystem.
# (c) BlankTB — All Rights Reserved 🌸

from fastapi import APIRouter, Query
from app.services import status_manager

# 🦌 Router Configuration
# (prefix handled in main.py)
router = APIRouter(tags=["Status"])

# 🌿🌸 ———————————————
#   PUBLIC ENDPOINTS
# ——————————————— 🌸🌿

# 🟢 PUBLIC STATUS
@router.get(
    "/public",
    summary="Public Status",
    description="Get the current live status of BlankTB services (🦌, 💾, 💌, etc.)"
)
async def public_status():
    """Return current cached public status summary for frontend display."""
    return await status_manager.get_cached_status()


# 📊 STATUS HISTORY
@router.get(
    "/history",
    summary="Get Status History",
    description="Fetch recorded service state changes for the past X hours (1–168)."
)
async def get_status_history(
    hours: int = Query(
        24,
        ge=1,
        le=168,
        description="Number of hours to view (1–168)."
    )
):
    """Return status history for all tracked services."""
    return await status_manager.get_history(range_hours=hours)


# 🧭 UPTIME PERCENTAGES
@router.get(
    "/uptime",
    summary="Get Uptime",
    description="View uptime percentage for each service over a specified number of days (1–30)."
)
async def get_uptime(
    days: int = Query(
        7,
        ge=1,
        le=30,
        description="Days to calculate uptime percentage (1–30)."
    )
):
    """Return uptime statistics for all monitored services."""
    return await status_manager.calculate_uptime(days=days)


# 🌈 DETAILED STATUS OVERVIEW
@router.get(
    "/details",
    summary="Detailed Status Overview",
    description="Provides uptime %, historical trend data, and summaries for each service."
)
async def get_detailed_status(
    days: int = Query(
        7,
        ge=1,
        le=30,
        description="Days of historical uptime data to include (1–30)."
    )
):
    """Return detailed service uptime and history for frontend graphs."""
    return await status_manager.get_detailed_status(days=days)


# 🧪 DEV TEST ALERT
@router.get(
    "/trigger-alert",
    summary="Trigger Test Alert",
    description="Send a manual test alert to the configured Discord webhook (developer-only)."
)
async def trigger_test_alert(
    service: str = "Backend",
    status: str = "offline"
):
    """
    Manually trigger a grouped Discord alert for developer testing.
    Confirms webhook configuration and embed styling.
    """
    # simulate one-service change format for test
    await status_manager.send_discord_alert({service: status})
    return {
        "status": "alert_sent",
        "service": service,
        "new_status": status,
        "note": "🦌 Webhook alert sent to Discord successfully!"
    }

# 🌸 End of BlankTB Status Router
