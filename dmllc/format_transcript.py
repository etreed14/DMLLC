import json
import os
import re
from google.cloud import storage


def list_json_blobs(bucket, prefix="transcripts/JSON"):
    return [
        blob
        for blob in bucket.list_blobs(prefix=prefix)
        if blob.name.lower().endswith(".json")
    ]


def flatten_word_info(data):
    words = []
    for result in data.get("results", []):
        alts = result.get("alternatives", [])
        if alts:
            for wi in alts[0].get("words", []):
                if "startTime" in wi:
                    words.append(wi)
    return words


def parse_seconds(time_str):
    m = re.match(r"([0-9]+(?:\.[0-9]+)?)s", time_str)
    return float(m.group(1)) if m else 0.0


def format_transcript(words):
    lines = []
    current_line = ""
    current_speaker = None
    current_min = -1
    for wi in words:
        word = wi.get("word", "")
        if not word:
            continue
        speaker = wi.get("speakerTag", 0)
        minute = int(parse_seconds(wi.get("startTime", "0s")) // 60)
        new_line = (speaker != current_speaker) or (minute != current_min)
        if new_line:
            if current_line:
                lines.append(current_line.strip())
            label = f"S{speaker}"
            if minute != current_min:
                label += f"|{minute}"
                current_min = minute
            current_line = f"{label} {word}"
            current_speaker = speaker
        else:
            if re.match(r"^[\.\!?,:;]+$", word):
                current_line += word
            else:
                current_line += f" {word}"
    if current_line:
        lines.append(current_line.strip())
    return "\n".join(lines)


def main(event=None, context=None):
    client = storage.Client()
    bucket = client.bucket("dmllc")
    for blob in list_json_blobs(bucket):
        data = json.loads(blob.download_as_text())
        words = flatten_word_info(data)
        formatted = format_transcript(words)
        base = os.path.basename(blob.name)
        if base.startswith("JSON_"):
            base = base[5:]
        out_name = "transcripts/" + os.path.splitext(base)[0] + ".txt"
        bucket.blob(out_name).upload_from_string(formatted, content_type="text/plain")
        print(f"Saved {out_name}")


if __name__ == "__main__":
    main()
