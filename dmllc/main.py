from flask import Flask, request
import requests
import json
from google.cloud import storage
import os
import logging
from tenacity import retry, wait_exponential, stop_after_attempt

logging.basicConfig(level=logging.INFO, format="%(message)s")

app = Flask(__name__)
storage_client = storage.Client()

# Output bucket and prefix
OUTPUT_BUCKET = os.environ.get("OUTPUT_BUCKET", "dmllc")
OUTPUT_PREFIX = os.environ.get("OUTPUT_PREFIX", "transcripts/")

# Google STT V2 endpoint
SPEECH_API_URL = os.environ.get(
    "SPEECH_API_URL",
    (
        "https://speech.googleapis.com/v2/projects/"
        "transcriptionpipeline-465613/locations/us-east1/recognizers/_:recognize"
    ),
)


@retry(wait=wait_exponential(multiplier=1), stop=stop_after_attempt(3))
def call_stt(token: str, payload: dict) -> requests.Response:
    return requests.post(
        SPEECH_API_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=payload,
    )


@app.route("/transcribe", methods=["POST"])
def transcribe():
    try:
        data = request.get_json()
        bucket = data.get("bucket")
        file_name = data.get("name")
        logging.info(
            json.dumps({"event": "request", "bucket": bucket, "file": file_name})
        )

        if not file_name or not file_name.lower().endswith((".mp3", ".wav")):
            logging.info(json.dumps({"event": "skip_non_audio", "file": file_name}))
            return "Not an audio file", 200

        gcs_uri = f"gs://{bucket}/{file_name}"
        logging.info(
            json.dumps({"event": "start_transcription", "gcs_uri": gcs_uri})
        )

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
            (
                "http://metadata.google.internal/computeMetadata/v1/instance/"
                "service-accounts/default/token"
            ),
            headers={"Metadata-Flavor": "Google"},
        )
        token = token_response.json().get("access_token")
        if not token:
            logging.error(json.dumps({"event": "token_error"}))
            return "Failed to get auth token", 500
        logging.info(json.dumps({"event": "token_acquired"}))

        # Call STT API with retry
        response = call_stt(token, payload)

        if response.status_code != 200:
            logging.error(
                json.dumps({"event": "stt_error", "status": response.status_code})
            )
            return f"Transcription failed: {response.text}", 500

        result = response.json()
        logging.info(json.dumps({"event": "stt_response"}))

        # Extract transcript
        transcript = ""
        for chunk in result.get("results", []):
            for alt in chunk.get("alternatives", []):
                transcript += alt.get("transcript", "") + "\n"

        if not transcript.strip():
            logging.info(json.dumps({"event": "empty_transcript"}))
            return "Transcript was empty", 200

        # Save .txt to OUTPUT_PREFIX folder in OUTPUT_BUCKET
        transcript_name = os.path.basename(file_name).rsplit(".", 1)[0] + ".txt"
        blob_path = f"{OUTPUT_PREFIX}{transcript_name}"
        blob = storage_client.bucket(OUTPUT_BUCKET).blob(blob_path)
        blob.upload_from_string(transcript)
        logging.info(
            json.dumps(
                {
                    "event": "transcript_saved",
                    "bucket": OUTPUT_BUCKET,
                    "path": blob_path,
                }
            )
        )

        return f"Transcript saved to {OUTPUT_BUCKET}/{blob_path}", 200

    except Exception as e:
        logging.exception("Error in /transcribe")
        return f"Server error: {str(e)}", 500


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
