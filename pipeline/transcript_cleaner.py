# pipeline/transcript_cleaner.py
"""
Optional transcript cleaning via generative AI.

This module defines a ``clean_transcript`` function that takes the output
of the initial formatting step and leverages a language model to correct
mis-recognised words, normalise numbers, and smooth awkward phrasing. If
no API key is provided, the function simply returns the input unchanged.

Prefers OpenAI (chat) via OPENAI_API_KEY. Falls back to Gemini if
GENAI_API_KEY is present. If neither is set, returns the input text.
"""

from __future__ import annotations

import logging
import os
from typing import List, Optional

logger = logging.getLogger(__name__)

# -----------------------------
# Provider selection & clients
# -----------------------------
USE_OPENAI = bool(os.getenv("OPENAI_API_KEY"))
USE_GEMINI = (not USE_OPENAI) and bool(os.getenv("GENAI_API_KEY"))

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
GENAI_MODEL = os.getenv("GENAI_MODEL", "gemini-1.5-flash")

_oai = None
_gmodel = None

if USE_OPENAI:
    # OpenAI (chat) path
    try:
        from openai import OpenAI  # openai>=1.40.0
        _oai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        logger.info("Transcript cleaner using OpenAI model %s", OPENAI_MODEL)
    except Exception as e:  # pragma: no cover
        logger.exception("Failed to init OpenAI client: %s", e)
        USE_OPENAI = False

if (not USE_OPENAI) and USE_GEMINI:
    # Gemini path
    try:
        import google.generativeai as genai  # type: ignore
        genai.configure(api_key=os.getenv("GENAI_API_KEY"))
        _gmodel = genai.GenerativeModel(GENAI_MODEL)
        logger.info("Transcript cleaner using Gemini model %s", GENAI_MODEL)
    except Exception as e:  # pragma: no cover
        logger.exception("Failed to init Gemini client: %s", e)
        USE_GEMINI = False


def _llm_generate(prompt: str) -> Optional[str]:
    """
    Return model text from OpenAI (preferred) or Gemini (fallback).
    Returns None if no provider is available or a call fails.
    """
    try:
        if USE_OPENAI and _oai:
            # Chat Completions
            r = _oai.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            txt = r.choices[0].message.content or ""
            return txt.strip() or None

        if USE_GEMINI and _gmodel:
            resp = _gmodel.generate_content(
                prompt,
                generation_config={"temperature": 0.2, "max_output_tokens": 4096},
            )
            txt = getattr(resp, "text", "") or ""
            return txt.strip() or None

        return None
    except Exception as exc:  # pragma: no cover
        logger.exception("LLM generate failed: %s", exc)
        return None


def clean_transcript(text: str, *, words: Optional[List[dict]] = None) -> str:
    """Clean and normalise a transcript using a language model.

    Args:
        text: The formatted transcript as produced by your formatter.
        words: Optional list of word dicts (unused in this baseline).

    Returns:
        A cleaned transcript, or the original text if no provider is available
        or the output looks suspicious.
    """
    if not (USE_OPENAI or USE_GEMINI):
        logger.info("No LLM configured; returning original text")
        return text

    prompt = (
        "You are a transcription cleaner. Given the transcript below, "
        "correct any mis-recognised words, normalise numbers, and ensure "
        "proper punctuation. Do not change speaker labels.\n\n"
        f"Transcript:\n{text}\n\nCleaned transcript:"
    )

    cleaned = _llm_generate(prompt)
    if not cleaned:
        logger.warning("LLM produced no output; using original transcript")
        return text

    # Basic sanity check: ensure labels (e.g., S1, S2) are not lost
    # (very rough heuristic; adjust if you use different labels)
    if cleaned.count("S") >= text.count("S"):
        return cleaned

    logger.warning("LLM output failed sanity check; using original")
    return text