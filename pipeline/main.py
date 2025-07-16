from flask import Flask, request
import requests
import json
from google.cloud import storage

app = Flask(__name__)
storage_client = storage.Client()

SPEECH_API_URL = "https://speech.googleapis.com/v2/projects/transcriptionpipeline-465613/locations/us-east1/recognizers/_:recognize"

@app.route("/transcribe", methods=["POST"])
def transcribe():
    data = request.get_json()
    bucket = data["bucket"]
    file_name = data["name"]

    if not (file_name.endswith(".mp3") or file_name.endswith(".wav")):
        return f"Skipping unsupported file: {file_name}", 200

    gcs_uri = f"gs://{bucket}/{file_name}"
    print(f"Processing {gcs_uri}")

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

    # Get metadata server access token
    try:
        token = requests.get(
            "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token",
            headers={"Metadata-Flavor": "Google"}
        ).json()["access_token"]
    except Exception as e:
        print(f"Error fetching token: {e}")
        return "Auth error", 500

    # STT v2 API request
    try:
        response = requests.post(
            SPEECH_API_URL,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json=payload
        )
        if response.status_code != 200:
            print(f"STT API error: {response.text}")
            return f"Transcription failed: {response.text}", 500
    except Exception as e:
        print(f"STT call error: {e}")
        return "Transcription request error", 500

    # Parse response
    result = response.json()
    print("Received STT response")

    transcript = ""
    for chunk in result.get("results", []):
        for alt in chunk.get("alternatives", []):
            transcript += alt.get("transcript", "") + "\n"

    if not transcript.strip():
        print("Empty transcript result")
        return "Transcript was empty", 200

    try:
        output_blob = storage_client.bucket(bucket).blob(f"Transcripts/{file_name.rsplit('.', 1)[0]}.txt")
        output_blob.upload_from_string(transcript)
        print(f"Saved to Transcripts/{file_name.rsplit('.', 1)[0]}.txt")
    except Exception as e:
        print(f"Error saving to GCS: {e}")
        return "Failed to save transcript", 500

    return f"Transcript saved for {file_name}", 200

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
