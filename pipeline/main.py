from flask import Flask, request
import requests
import json
from google.cloud import storage
import pathlib, time, threading, subprocess


def _watch_for_mp3s(poll_seconds: int = 20):
    aud_dir = pathlib.Path("audios")
    out_dir = pathlib.Path("Transcripts")
    out_dir.mkdir(exist_ok=True)

    print("[watcher] running, polling", poll_seconds, "s", flush=True)

    while True:
        for mp3 in aud_dir.glob("*.mp3"):
            tgt = out_dir / f"{mp3.stem}.txt"
            if tgt.exists():
                continue
            try:
                print("[watcher] transcribing", mp3.name, flush=True)
                txt = subprocess.check_output(
                    ["python", "pipeline/transcribe.py", str(mp3)]
                ).decode()
                tgt.write_text(txt)
                print("[watcher] ✅", tgt.name, "written", flush=True)
            except Exception as e:
                print("[watcher] ❌", mp3.name, "→", e, flush=True)
        time.sleep(poll_seconds)

app = Flask(__name__)
storage_client = storage.Client()

# Google STT V2 endpoint
SPEECH_API_URL = "https://speech.googleapis.com/v2/projects/transcriptionpipeline-465613/locations/us-east1/recognizers/_:recognize"

@app.route("/transcribe", methods=["POST"])
def transcribe():
    try:
        data = request.get_json()
        bucket = data["bucket"]
        file_name = data["name"]

        if not file_name.lower().endswith((".mp3", ".wav")):
            print(f"Skipping non-audio file: {file_name}")
            return "Not an audio file", 200

        gcs_uri = f"gs://{bucket}/{file_name}"
        print(f"Starting transcription for: {gcs_uri}")

        # Prepare STT V2 payload
        payload = {
            "config": {
                "autoDecodingConfig": {},
                "features": {
                    "enableAutomaticPunctuation": True,
                    "enableSpeakerDiarization": True,
                    "diarizationSpeakerCount": 2
                }
            },
            "uri": gcs_uri
        }

        # Retrieve token from metadata server
        token_response = requests.get(
            "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token",
            headers={"Metadata-Flavor": "Google"}
        )
        token = token_response.json().get("access_token")
        if not token:
            print("No token found in metadata response.")
            return "Failed to get auth token", 500

        # Call STT API
        response = requests.post(
            SPEECH_API_URL,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json=payload
        )

        if response.status_code != 200:
            print(f"STT API error:\n{response.text}")
            return f"Transcription failed: {response.text}", 500

        result = response.json()
        print("Received STT response.")

        # Extract transcript
        transcript = ""
        for chunk in result.get("results", []):
            for alt in chunk.get("alternatives", []):
                transcript += alt.get("transcript", "") + "\n"

        if not transcript.strip():
            print("Empty transcript result.")
            return "Transcript was empty", 200

        # Save .txt to Transcripts/ folder
        transcript_name = file_name.rsplit(".", 1)[0] + ".txt"
        blob_path = f"Transcripts/{transcript_name}"
        blob = storage_client.bucket(bucket).blob(blob_path)
        blob.upload_from_string(transcript)
        print(f"Saved transcript to {blob_path}")

        return f"Transcript saved to {blob_path}", 200

    except Exception as e:
        import traceback
        print("=== ERROR OCCURRED DURING /transcribe ===")
        traceback.print_exc()
        return f"Server error: {str(e)}", 500

if __name__ == "__main__":
    import os
    threading.Thread(target=_watch_for_mp3s, daemon=True).start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
