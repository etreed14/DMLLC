from flask import Flask, request
import requests
import json
from google.cloud import storage

app = Flask(__name__)
storage_client = storage.Client()

# GOOGLE API V2 endpoint
SPEECH_API_URL = "https://speech.googleapis.com/v2/projects/transcriptionpipeline-465613/locations/us-east1/recognizers/_:recognize"

@app.route("/transcribe", methods=["POST"])
def transcribe():
    data = request.get_json()
    bucket = data["bucket"]
    file_name = data["name"]

    if not file_name.endswith(".wav"):
        return "Not a WAV file", 200

    gcs_uri = f"gs://{bucket}/{file_name}"

    headers = {"Content-Type": "application/json"}
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

    # Get access token from metadata server
    token = requests.get(
        "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token",
        headers={"Metadata-Flavor": "Google"}
    ).json()["access_token"]

    # Call STT V2 API
    response = requests.post(
        SPEECH_API_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json=payload
    )

    if response.status_code != 200:
        return f"Transcription failed: {response.text}", 500

    result = response.json()
    transcript = ""

    for chunk in result.get("results", []):
        for alt in chunk.get("alternatives", []):
            transcript += alt.get("transcript", "") + "\n"

    # Save to GCS as .txt
    output_blob = storage_client.bucket(bucket).blob(file_name.replace(".wav", ".txt"))
    output_blob.upload_from_string(transcript)

    return f"Transcript saved for {file_name}", 200

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)