#!/usr/bin/env python3
# 🦌 BlankTB Portal — Status Helper
# Shared utilities for checking service availability.
# (c) BlankTB — All Rights Reserved

import aiohttp, asyncio

async def check_service(url: str, timeout: float = 3.0) -> str:
    """Ping a given service URL and return simplified status."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=timeout) as resp:
                if 200 <= resp.status < 400:
                    return "operational"
                elif 400 <= resp.status < 500:
                    return "degraded"
                else:
                    return "offline"
    except asyncio.TimeoutError:
        return "offline"
    except Exception:
        return "offline"
