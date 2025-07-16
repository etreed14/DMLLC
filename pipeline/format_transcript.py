import json
import re
from google.cloud import storage

BUCKET_NAME = "dmllc"
INPUT_JSON_BLOB = "transcripts/ONON, DECK \\u0026 NKE Lacing Up for 2H25_transcript_*.json"  # update wildcard or filename
OUTPUT_TXT_BLOB = "formatted/ONON_DECK_NKE_2H25.txt"  # change output path as needed

client = storage.Client()

def download_json_blob(bucket_name, blob_prefix):
    bucket = client.bucket(bucket_name)
    blobs = list(client.list_blobs(bucket, prefix=blob_prefix.replace('\\u0026', '&').split('*')[0]))
    for blob in blobs:
        if blob.name.endswith(".json"):
            content = blob.download_as_text()
            return json.loads(content)
    raise FileNotFoundError("Transcript JSON not found.")

def format_transcript(json_data):
    results = json_data.get("results", [])
    if not results:
        return ""

    words_info = results[0]["alternatives"][0]["words"]
    formatted_lines = []
    current_minute = -1
    current_line = ""
    current_speaker = None

    for word_info in words_info:
        word = word_info["word"]
        start_time = word_info.get("startTime", "0s")
        speaker_tag = word_info.get("speakerTag", 0)
        seconds = float(re.match(r"(\d+)", start_time).group(1)) if re.match(r"\d+", start_time) else 0
        minute = int(seconds // 60)

        # If speaker changed, start new line
        if speaker_tag != current_speaker:
            if current_line:
                formatted_lines.append(current_line.strip())
            label = f"S{speaker_tag if speaker_tag else 0}"
            if minute != current_minute:
                label += f"|{minute}"
            current_line = f"{label} {word}"
            current_speaker = speaker_tag
            current_minute = minute
        else:
            # Insert minute tag mid-line if minute changed
            if minute != current_minute:
                current_line += f"\nS{speaker_tag if speaker_tag else 0}|{minute} {word}"
                current_minute = minute
            else:
                current_line += f" {word}"

    if current_line:
        formatted_lines.append(current_line.strip())

    return "\n".join(formatted_lines)

def upload_txt_to_gcs(text, bucket_name, output_blob_name):
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(output_blob_name)
    blob.upload_from_string(text, content_type="text/plain")
    print(f"Formatted transcript saved to: gs://{bucket_name}/{output_blob_name}")

def main():
    json_data = download_json_blob(BUCKET_NAME, INPUT_JSON_BLOB)
    formatted_text = format_transcript(json_data)
    upload_txt_to_gcs(formatted_text, BUCKET_NAME, OUTPUT_TXT_BLOB)

if __name__ == "__main__":
    main()
