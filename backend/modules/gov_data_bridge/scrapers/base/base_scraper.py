"""Base Scraper - Abstract base class for all state scrapers"""
import os
import asyncio
import hashlib
import logging
from datetime import datetime, timezone
from abc import ABC, abstractmethod
from typing import Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger("govdatabridge")

GOV_MOCK_MODE = os.environ.get("GOV_MOCK_MODE", "true").lower() == "true"
RATE_LIMIT = int(os.environ.get("GOV_RATE_LIMIT_PER_PORTAL", "10"))


class BaseScraper(ABC):
    """Abstract base scraper - all state scrapers extend this."""

    def __init__(self, portal_config: dict):
        self.config = portal_config
        self.name = portal_config["name"]
        self.url = portal_config["url"]
        self.captcha_type = portal_config.get("captcha_type", "none")
        self.scraper_type = portal_config.get("scraper_type", "httpx")
        self._last_request_time = 0
        self._client = None

    async def init(self):
        """Initialize HTTP client"""
        if not self._client:
            self._client = httpx.AsyncClient(
                timeout=30.0,
                follow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def respect_rate_limit(self):
        """Rate limit requests per portal"""
        now = asyncio.get_event_loop().time()
        min_interval = 1.0 / RATE_LIMIT
        elapsed = now - self._last_request_time
        if elapsed < min_interval:
            await asyncio.sleep(min_interval - elapsed)
        self._last_request_time = asyncio.get_event_loop().time()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=60))
    async def with_retry(self, fn, *args, **kwargs):
        """Execute with retry and exponential backoff"""
        return await fn(*args, **kwargs)

    async def navigate_to(self, url: str) -> httpx.Response:
        """Navigate to URL with rate limiting"""
        await self.respect_rate_limit()
        await self.init()
        return await self._client.get(url)

    async def post_form(self, url: str, data: dict) -> httpx.Response:
        """POST form data"""
        await self.respect_rate_limit()
        await self.init()
        return await self._client.post(url, data=data)

    async def solve_captcha(self, image_bytes: bytes) -> str:
        """Solve CAPTCHA using the captcha solver"""
        from modules.gov_data_bridge.captcha.captcha_solver import CaptchaSolver
        solver = CaptchaSolver()
        return await solver.solve(image_bytes)

    async def fetch(self, inputs: dict, document_type: str) -> dict:
        """Main fetch method - routes to mock or live mode"""
        if GOV_MOCK_MODE:
            return await self.fetch_mock(inputs, document_type)
        return await self.fetch_live(inputs, document_type)

    async def fetch_live(self, inputs: dict, document_type: str) -> dict:
        """Live scraping - override per state for real implementation"""
        try:
            await self.init()
            await self.respect_rate_limit()
            return await self.extract_data(inputs, document_type)
        except Exception as e:
            logger.error(f"[{self.name}] Live fetch failed: {e}")
            raise

    @abstractmethod
    async def extract_data(self, inputs: dict, document_type: str) -> dict:
        """State-specific data extraction - MUST override"""
        pass

    @abstractmethod
    async def fetch_mock(self, inputs: dict, document_type: str) -> dict:
        """Return realistic mock data - MUST override"""
        pass

    def generate_deterministic_seed(self, inputs: dict) -> int:
        """Generate a deterministic seed from inputs for consistent mock data"""
        key = "".join(str(v) for v in inputs.values())
        return int(hashlib.md5(key.encode()).hexdigest()[:8], 16)

    def build_result(self, document_type: str, structured_data: dict, pdf_available: bool = True) -> dict:
        """Standard result format"""
        return {
            "state": self.config.get("state_key", ""),
            "portal_name": self.name,
            "portal_url": self.url,
            "document_type": document_type,
            "structured_data": structured_data,
            "pdf_available": pdf_available,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "source": "mock" if GOV_MOCK_MODE else "live",
            "status": "success",
        }

    async def check_portal_health(self) -> dict:
        """Check if the portal is reachable"""
        try:
            await self.init()
            resp = await self._client.get(self.url, timeout=10.0)
            return {
                "state": self.name,
                "url": self.url,
                "status": "UP" if resp.status_code < 400 else "DOWN",
                "response_time_ms": resp.elapsed.total_seconds() * 1000 if resp.elapsed else 0,
                "status_code": resp.status_code,
            }
        except Exception as e:
            return {"state": self.name, "url": self.url, "status": "DOWN", "error": str(e)}
