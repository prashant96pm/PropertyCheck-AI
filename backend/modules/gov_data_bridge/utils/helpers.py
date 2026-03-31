"""Utility modules for GovDataBridge"""
import asyncio
import logging
from datetime import datetime, timezone

logger = logging.getLogger("govdatabridge")


class PortalHealthChecker:
    """Check health status of all government portals"""

    _cache = {}
    _cache_ttl = 300  # 5 minutes

    @classmethod
    async def check_all(cls, portals: dict) -> dict:
        """Check all portals and return status map"""
        from modules.gov_data_bridge.scrapers import get_scraper

        now = datetime.now(timezone.utc).timestamp()
        results = {}

        for state_key in portals:
            cached = cls._cache.get(state_key)
            if cached and (now - cached.get("checked_at", 0)) < cls._cache_ttl:
                results[state_key] = cached
                continue

            scraper = get_scraper(state_key)
            if scraper:
                try:
                    health = await scraper.check_portal_health()
                    health["checked_at"] = now
                    cls._cache[state_key] = health
                    results[state_key] = health
                except Exception:
                    results[state_key] = {"state": state_key, "status": "UNKNOWN", "checked_at": now}
            else:
                results[state_key] = {"state": state_key, "status": "NO_SCRAPER", "checked_at": now}

            await scraper.close() if scraper else None

        return results

    @classmethod
    async def check_single(cls, state_key: str) -> dict:
        """Check a single portal"""
        from modules.gov_data_bridge.scrapers import get_scraper
        scraper = get_scraper(state_key)
        if not scraper:
            return {"state": state_key, "status": "NO_SCRAPER"}
        try:
            result = await scraper.check_portal_health()
            return result
        finally:
            await scraper.close()


class RateLimiter:
    """Per-portal rate limiting"""
    _windows = {}

    @classmethod
    async def acquire(cls, portal_key: str, max_per_minute: int = 10):
        """Wait if rate limit exceeded"""
        now = asyncio.get_event_loop().time()
        window = cls._windows.setdefault(portal_key, [])
        window[:] = [t for t in window if now - t < 60]
        if len(window) >= max_per_minute:
            wait_time = 60 - (now - window[0])
            logger.info(f"Rate limit hit for {portal_key}, waiting {wait_time:.1f}s")
            await asyncio.sleep(wait_time)
        window.append(now)
