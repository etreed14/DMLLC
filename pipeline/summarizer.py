# pipeline/summarizer.py
"""
Transcript summarisation utilities.

Prefers OpenAI chat if OPENAI_API_KEY is set; otherwise falls back to
Gemini if GENAI_API_KEY is set. You can customize the prompt with the
SUMMARISER_PROMPT environment variable.
"""

from __future__ import annotations

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# -----------------------------
# Provider selection & clients
# -----------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GENAI_API_KEY = os.getenv("GENAI_API_KEY")

USE_OPENAI = bool(OPENAI_API_KEY)
USE_GEMINI = (not USE_OPENAI) and bool(GENAI_API_KEY)

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
GENAI_MODEL = os.getenv("GENAI_MODEL", "gemini-1.5-flash")

_oai = None
_gmodel = None

if USE_OPENAI:
    try:
        from openai import OpenAI  # requires openai>=1.40.0
        _oai = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("Summariser using OpenAI model %s", OPENAI_MODEL)
    except Exception as e:  # pragma: no cover
        logger.exception("Failed to init OpenAI client: %s", e)
        USE_OPENAI = False

if (not USE_OPENAI) and USE_GEMINI:
    try:
        import google.generativeai as genai  # type: ignore
        genai.configure(api_key=GENAI_API_KEY)
        _gmodel = genai.GenerativeModel(GENAI_MODEL)
        logger.info("Summariser using Gemini model %s", GENAI_MODEL)
    except Exception as e:  # pragma: no cover
        logger.exception("Failed to init Gemini client: %s", e)
        USE_GEMINI = False


DEFAULT_PROMPT = (
    "You are an expert meeting summariser. Summarise the following "
    "transcript into a concise report including:\n"
    "• An executive summary of key points\n"
    "• A list of action items\n"
    "• Any important dates, deadlines or follow-ups\n"
    "Use bullet points and keep the summary under 300 words.\n\n"
    "Transcript:\n{transcript}\n\nSummary:"
)


def _llm_generate(prompt: str) -> Optional[str]:
    """Return text from OpenAI (preferred) or Gemini (fallback)."""
    try:
        if USE_OPENAI and _oai:
            r = _oai.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            txt = r.choices[0].message.content or ""
            return txt.strip() or None

        if USE_GEMINI and _gmodel:
            resp = _gmodel.generate_content(
                prompt,
                generation_config={"temperature": 0.3, "max_output_tokens": 1024},
            )
            txt = getattr(resp, "text", "") or ""
            return txt.strip() or None

        return None
    except Exception as exc:  # pragma: no cover
        logger.exception("LLM generate failed (summariser): %s", exc)
        return None


def summarise(text: str) -> str:
    """Generate a summary for the given transcript.

    Returns empty string if no LLM is configured or the call fails.
    """
    if not text.strip():
        return ""

    if not (USE_OPENAI or USE_GEMINI):
        logger.warning("No generative AI available; cannot generate summary")
        return ""

    prompt_template = os.environ.get("SUMMARISER_PROMPT", DEFAULT_PROMPT)
    prompt = prompt_template.format(transcript=text)

    out = _llm_generate(prompt)
    if out:
        return out

    logger.warning("Summariser produced no output; returning empty string")
    return ""