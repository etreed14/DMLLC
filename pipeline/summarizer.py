"""
Transcript summarisation utilities.

This module provides a function to summarise cleaned transcripts using
generative models.  It supports Gemini via the ``google-generativeai``
library by default but can be adapted to other providers by modifying
``_call_model``.  The summary prompt can be customised through the
``SUMMARISER_PROMPT`` environment variable.
"""

from __future__ import annotations

import logging
import os
from typing import Optional

try:
    import google.generativeai as genai  # type: ignore[import-not-found]
    _GENAI_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    _GENAI_AVAILABLE = False

logger = logging.getLogger(__name__)


DEFAULT_PROMPT = (
    "You are an expert meeting summariser.  Summarise the following "
    "transcript into a concise report including:\n"
    "• An executive summary of key points\n"
    "• A list of action items\n"
    "• Any important dates, deadlines or follow‑ups\n"
    "Use bullet points and keep the summary under 300 words.\n\n"
    "Transcript:\n{transcript}\n\nSummary:"
)


def summarise(text: str) -> str:
    """Generate a summary for the given transcript.

    Args:
        text: The cleaned transcript to summarise.

    Returns:
        A summary string.  If no generative model is available, the
        function returns an empty string.
    """
    api_key = os.environ.get("GENAI_API_KEY")
    if not api_key or not _GENAI_AVAILABLE:
        logger.warning("No generative AI available; cannot generate summary")
        return ""
    genai.configure(api_key=api_key)
    model_name = os.environ.get("GENAI_MODEL", "models/gemini-pro")
    prompt_template = os.environ.get("SUMMARISER_PROMPT", DEFAULT_PROMPT)
    prompt = prompt_template.format(transcript=text)
    try:
        logger.info("Calling generative model %s for summarisation", model_name)
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.4, "max_output_tokens": 1024},
        )
        return response.text.strip()
    except Exception as exc:  # pragma: no cover - network errors
        logger.exception("Error generating summary: %s", exc)
        return ""
