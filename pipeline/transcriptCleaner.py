"""
Optional transcript cleaning via generative AI.

This module defines a ``cleanTranscript`` function that takes the output
of the initial formatting step and leverages a language model to correct
mis‑recognised words, normalise numbers, and smooth awkward phrasing.
If no API key is provided, the function simply returns the input unchanged.
"""

from __future__ import annotations

import logging
import os
from typing import List, Optional

try:
    import google.generativeai as genai  # type: ignore[import-not-found]
    _GENAI_AVAILABLE = True
except ImportError:
    _GENAI_AVAILABLE = False

logger = logging.getLogger(__name__)


def cleanTranscript(text: str, *, words: Optional[List[dict]] = None) -> str:
    """Clean and normalise a transcript using a language model."""
    apiKey = os.environ.get("GENAI_API_KEY")
    if not apiKey or not _GENAI_AVAILABLE:
        logger.info("No generative AI available; returning original text")
        return text
    genai.configure(api_key=apiKey)
    modelName = os.environ.get("GENAI_MODEL", "models/gemini-pro")
    try:
        logger.info("Calling generative model %s for transcript cleaning", modelName)
        model = genai.GenerativeModel(modelName)
        prompt = (
            "You are a transcription cleaner.  Given the transcript below, "
            "correct any mis‑recognised words, normalise numbers and ensure "
            "proper punctuation.  Do not change speaker labels.\n\n"
            f"Transcript:\n{text}\n\nCleaned transcript:"
        )
        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.2, "max_output_tokens": 4096},
        )
        cleaned = response.text.strip()
        if cleaned and cleaned.count("S") >= text.count("S"):
            return cleaned
        logger.warning("Generative model returned unexpected output; using original")
        return text
    except Exception as exc:
        logger.exception("Error cleaning transcript: %s", exc)
        return text
