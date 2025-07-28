"""
Transcript formatting utilities.

The Speech‑to‑Text API returns a deeply nested structure where words are
nested within alternatives and results.  The functions in this module
flatten that structure and rebuild it into a more human‑readable format.

The default formatter groups consecutive words by speaker tag and the minute
of the recording in which they occur.  Each line begins with a label
such as ``S1|3`` meaning “Speaker 1 at minute 3”.
"""

import re
from typing import Dict, Iterable, List


def flattenWordInfo(data: Dict) -> List[Dict]:
    """Extract a flat list of word dictionaries from a STT response."""
    words: List[Dict] = []
    for result in data.get("results", []):
        alternatives = result.get("alternatives", [])
        if not alternatives:
            continue
        for wi in alternatives[0].get("words", []):
            if "word" in wi:
                words.append(wi)
    return words


def _parseSeconds(timeStr: str) -> float:
    match = re.match(r"([0-9]+(?:\.[0-9]+)?)s", timeStr)
    return float(match.group(1)) if match else 0.0


def formatTranscript(words: Iterable[Dict]) -> str:
    """Convert a flat list of word dictionaries into a labelled transcript."""
    lines: List[str] = []
    currentLine = ""
    currentSpeaker: int | None = None
    currentMinute = -1
    for wi in words:
        word = wi.get("word", "")
        if not word:
            continue
        speaker = wi.get("speakerTag", 0)
        minute = int(_parseSeconds(wi.get("startTime", "0s")) // 60)
        newGroup = (speaker != currentSpeaker) or (minute != currentMinute)
        if newGroup:
            if currentLine:
                lines.append(currentLine.strip())
            label = f"S{speaker}"
            if minute != currentMinute:
                label += f"|{minute}"
                currentMinute = minute
            currentLine = f"{label} {word}"
            currentSpeaker = speaker
        else:
            if re.match(r"^[\.!?,:;]+$", word):
                currentLine += word
            else:
                currentLine += f" {word}"
    if currentLine:
        lines.append(currentLine.strip())
    return "\n".join(lines)
