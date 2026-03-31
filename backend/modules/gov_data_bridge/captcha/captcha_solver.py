"""CAPTCHA Solver - 2Captcha API + OCR fallback + mock bypass (3-tier fallback)"""
import os
import io
import logging

logger = logging.getLogger("govdatabridge")

CAPTCHA_PROVIDER = os.environ.get("CAPTCHA_PROVIDER", "auto")
TWOCAPTCHA_API_KEY = os.environ.get("TWOCAPTCHA_API_KEY", "").strip()


class CaptchaSolver:
    """Solve CAPTCHAs with 3-tier fallback: 2Captcha → OCR → Mock"""

    def __init__(self):
        self._provider = self._determine_provider()

    def _determine_provider(self) -> str:
        if CAPTCHA_PROVIDER == "2captcha" and TWOCAPTCHA_API_KEY:
            return "2captcha"
        if CAPTCHA_PROVIDER == "ocr":
            return "ocr"
        if CAPTCHA_PROVIDER == "mock":
            return "mock"
        # auto: try 2captcha if key exists, else OCR, else mock
        if TWOCAPTCHA_API_KEY:
            return "2captcha"
        return "ocr"

    async def solve(self, image_bytes: bytes) -> str:
        """Solve a CAPTCHA image with fallback chain"""
        if self._provider == "2captcha":
            result = await self._twocaptcha_solve(image_bytes)
            if result:
                return result
            logger.info("2Captcha failed, falling back to OCR")

        if self._provider in ("2captcha", "ocr"):
            result = await self._ocr_solve(image_bytes)
            if result:
                return result
            logger.info("OCR failed, falling back to mock")

        return self._mock_solve()

    async def _twocaptcha_solve(self, image_bytes: bytes) -> str:
        """Solve using 2Captcha API"""
        try:
            import base64
            import httpx

            b64 = base64.b64encode(image_bytes).decode()
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Submit CAPTCHA
                resp = await client.post("https://2captcha.com/in.php", data={
                    "key": TWOCAPTCHA_API_KEY,
                    "method": "base64",
                    "body": b64,
                    "json": 1,
                })
                data = resp.json()
                if data.get("status") != 1:
                    logger.warning(f"2Captcha submit failed: {data}")
                    return None

                captcha_id = data["request"]

                # Poll for result
                import asyncio
                for _ in range(20):
                    await asyncio.sleep(5)
                    resp = await client.get(f"https://2captcha.com/res.php?key={TWOCAPTCHA_API_KEY}&action=get&id={captcha_id}&json=1")
                    data = resp.json()
                    if data.get("status") == 1:
                        logger.info(f"2Captcha solved: {data['request'][:10]}...")
                        return data["request"]
                    if data.get("request") != "CAPCHA_NOT_READY":
                        logger.warning(f"2Captcha error: {data}")
                        return None

                logger.warning("2Captcha timeout")
                return None
        except Exception as e:
            logger.error(f"2Captcha error: {e}")
            return None

    async def _ocr_solve(self, image_bytes: bytes) -> str:
        """OCR-based CAPTCHA solving using pytesseract + Pillow"""
        try:
            from PIL import Image, ImageFilter, ImageEnhance
            import pytesseract

            img = Image.open(io.BytesIO(image_bytes))
            img = img.convert("L")
            img = ImageEnhance.Contrast(img).enhance(2.5)
            img = img.filter(ImageFilter.MedianFilter(size=3))
            img = img.point(lambda x: 0 if x < 128 else 255)

            text = pytesseract.image_to_string(
                img, config="--psm 7 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
            ).strip()

            if text and len(text) >= 3:
                logger.info(f"OCR CAPTCHA solved: {text}")
                return text
            logger.warning(f"OCR result too short: '{text}'")
            return None
        except ImportError:
            logger.warning("pytesseract not available")
            return None
        except Exception as e:
            logger.error(f"CAPTCHA OCR error: {e}")
            return None

    def _mock_solve(self) -> str:
        """Mock CAPTCHA bypass for development"""
        return "MOCK123"

    def get_provider_info(self) -> dict:
        return {
            "configured_provider": CAPTCHA_PROVIDER,
            "active_provider": self._provider,
            "twocaptcha_configured": bool(TWOCAPTCHA_API_KEY),
        }
