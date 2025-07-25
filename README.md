# DMLLC Pipeline V3
![CI](https://github.com/OWNER/REPO/actions/workflows/test.yml/badge.svg)

### 🏁 Pipeline Flow

```
audio file -> GCS bucket -> Cloud Function -> raw JSON -> formatter -> transcript
```

### Audios

- User drops an .mp3 or .wav audio file into the audios/ folder in Google Cloud Storage.
- This upload automatically triggers the pipeline.
- Audio .mp3 files are converted to .wav files for processing
- Converted audio files are sent to transcription phase 1

### 🏎️ Raw Transcription

- Uses **Google Speech-to-Text v2** (with punctuation + speaker diarization enabled)
- Transcription results are returned in structured JSON format with confidense levels.
- Converted audio files are sent to transcription phase 2

### ⛵ Clean Transcription

- **Gemini 2.5** uses confidense levels and context to clean up words/phrasing throughout transcript
- A post-processing script formats transcripts into clean, readable text.
- Speaker turns are labeled, punctuation is finalized.
- Long silences/irrelevant segments may be removed/merged.
- Transcripts are saved in the Transcripts/ folder.

### 🛩️ Summarize

- Trigger call pulls transript when added to folder
- A summarization script produces an overview of the call or meeting.
- Key themes or highlights are extracted based on custom Gemini 2.5 prompts.
- Output summaries are saved in the DMLLC/Summaries/ folder.

### 🚀 Email (Next Version)
- Trigger call pulls summaries when added to folder
- Google email client creates email and adds summary
- Summary is sent to jdematteo@dmllc.com & email who uploaded original transcript

### 🪐 Portal (Next Next Version)
- Confirmed summaries are converted to custom html-formatted docs
- Matched html text is uploaded to site and formatted under relevant meeting section

## Local Development

1. Copy `.env.example` to `.env` and update the values for your project.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Flask service locally:
   ```bash
   python dmllc/main.py
   ```
4. To test the Cloud Function locally, invoke `transcribe_audio.transcribe_audio` with a mock event.

## Environment Variables

The following variables configure the pipeline:

| Name | Description |
| ---- | ----------- |
| `OUTPUT_BUCKET` | Bucket where transcripts are written |
| `OUTPUT_PREFIX` | Folder prefix for text transcripts |
| `AUDIO_PREFIX` | Folder prefix for uploaded audio |
| `TRANSCRIPTS_PREFIX` | Folder prefix for intermediate results |
| `SPEECH_API_URL` | Google Speech-to-Text v2 endpoint |

Create a `.env` file based on `.env.example` when running locally.

## Deployment

`cloudbuild.yaml` builds the Docker image and the Cloud Build trigger defined in `trigger.yaml` deploys on pushes to the `main` branch. Ensure the service account has permission to access Storage and Speech-to-Text APIs.

GitHub Actions (`.github/workflows/`) run linting and tests on every push.

The project structure is:

```
dmllc/               Flask app and Cloud Function code
audios/              Sample audio files
Dockerfile           Container for running the Flask service
```
