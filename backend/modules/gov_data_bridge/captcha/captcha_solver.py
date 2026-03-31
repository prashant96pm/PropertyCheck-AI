"""CAPTCHA Solver - OCR-based local solver with mock bypass"""
import os
import io
import logging

logger = logging.getLogger("govdatabridge")
GOV_MOCK_MODE = os.environ.get("GOV_MOCK_MODE", "true").lower() == "true"


class CaptchaSolver:
    """Solve CAPTCHAs using pytesseract OCR or mock bypass"""

    def __init__(self):
        self.mock_mode = GOV_MOCK_MODE

    async def solve(self, image_bytes: bytes) -> str:
        """Solve a CAPTCHA image. Returns the text."""
        if self.mock_mode:
            return self._mock_solve()
        return await self._ocr_solve(image_bytes)

    def _mock_solve(self) -> str:
        """Mock CAPTCHA bypass for development"""
        return "MOCK123"

    async def _ocr_solve(self, image_bytes: bytes) -> str:
        """OCR-based CAPTCHA solving using pytesseract + Pillow"""
        try:
            from PIL import Image, ImageFilter, ImageEnhance
            import pytesseract

            img = Image.open(io.BytesIO(image_bytes))

            # Preprocessing pipeline
            img = img.convert("L")  # Grayscale
            img = ImageEnhance.Contrast(img).enhance(2.5)  # High contrast
            img = img.filter(ImageFilter.MedianFilter(size=3))  # Denoise
            img = img.point(lambda x: 0 if x < 128 else 255)  # Binarize

            text = pytesseract.image_to_string(
                img, config="--psm 7 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
            ).strip()

            logger.info(f"OCR CAPTCHA solved: {text}")
            return text
        except ImportError:
            logger.warning("pytesseract not available, using mock")
            return self._mock_solve()
        except Exception as e:
            logger.error(f"CAPTCHA OCR error: {e}")
            return self._mock_solve()
