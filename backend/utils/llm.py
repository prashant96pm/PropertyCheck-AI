"""Thin async wrapper around the Google Gemini API (google-genai SDK)."""
from typing import Optional
from config import GEMINI_API_KEY, GEMINI_MODEL, logger

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

_client = None

LLM_ENABLED = bool(GEMINI_API_KEY and genai)


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


async def generate_text(prompt: str, system_message: Optional[str] = None, model: Optional[str] = None) -> Optional[str]:
    """Send a single-turn prompt to Gemini and return the response text.

    Returns None when the LLM is not configured. Raises on API errors so callers
    can fall back to their rule-based logic.
    """
    if not LLM_ENABLED:
        return None
    config = types.GenerateContentConfig(system_instruction=system_message) if system_message else None
    response = await _get_client().aio.models.generate_content(
        model=model or GEMINI_MODEL,
        contents=prompt,
        config=config,
    )
    return response.text or ""
