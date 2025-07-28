"""
Transcript formatting utilities.

The Speech‑to‑Text API returns a deeply nested structure where words are
nested within alternatives and results.  The functions in this module
flatten that structure and rebuild it into a more human‑readable format.

The default formatter groups consecutive words by speaker tag and minute.
Each line begins with a label such as ``S1|3`` meaning “Speaker 1 at
minute 3”.  You can customise this behaviour by altering the grouping logic.
"""

import re
from typing import Dict, Iterable, List


def flatten_word_info(data: Dict) -> List[Dict]:
    """Extract a flat list of word dictionaries from a STT response.

    Args:
        data: Parsed JSON dictionary returned from the Speech‑to‑Text API.

    Returns:
        A list of word dictionaries.  Each dictionary contains keys like
        ``word``, ``startTime``, ``endTime``, ``confidence`` and
        ``speakerTag``.
    """
    words: List[Dict] = []
    for result in data.get("results", []):
        alternatives = result.get("alternatives", [])
        if not alternatives:
            continue
        # Use the first alternative, which is typically the most probable.
        for wi in alternatives[0].get("words", []):
            if "word" in wi:
                words.append(wi)
    return words


def _parse_seconds(time_str: str) -> float:
    match = re.match(r"([0-9]+(?:\.[0-9]+)?)s", time_str)
    return float(match.group(1)) if match else 0.0


def format_transcript(words: Iterable[Dict]) -> str:
    """Convert a flat list of word dictionaries into a labelled transcript.

    Words are grouped by speaker tag and the minute of the recording in
    which they occur.  The first word of each group starts a new line with
    a label (``S1`` for speaker 1, optionally suffixed with ``|minute``).

    Args:
        words: An iterable of word dictionaries as returned by
            :func:`flatten_word_info`.

    Returns:
        A single string containing the formatted transcript.
    """
    lines: List[str] = []
    current_line = ""
    current_speaker: int | None = None
    current_minute = -1
    for wi in words:
        word = wi.get("word", "")
        if not word:
            continue
        speaker = wi.get("speakerTag", 0)
        minute = int(_parse_seconds(wi.get("startTime", "0s")) // 60)
        new_group = (speaker != current_speaker) or (minute != current_minute)
        if new_group:
            if current_line:
                lines.append(current_line.strip())
            label = f"S{speaker}"
            if minute != current_minute:
                label += f"|{minute}"
                current_minute = minute
            current_line = f"{label} {word}"
            current_speaker = speaker
        else:
            # Append punctuation directly without a preceding space
            if re.match(r"^[\.!?,:;]+$", word):
                current_line += word
            else:
                current_line += f" {word}"
    if current_line:
        lines.append(current_line.strip())
    return "\n".join(lines)
