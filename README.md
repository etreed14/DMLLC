# Transcription Pipeline – Improved Design

## Overview

This repository contains an end‑to‑end audio‑to‑insight pipeline designed to be
easy for non‑technical users while still providing flexibility for engineers.
Users simply drop audio files into the **Audios/** folder and retrieve finished
transcripts and summaries from the **Transcripts/** folder.  All of the
processing logic lives inside the **pipeline/** package.

### Workflow

1. **Upload Audio** – A user copies an `.mp3`, `.m4a` or `.wav` file into the
   **Audios/** folder in your Cloud Storage bucket.  The file name should
   contain a date (e.g. `2025‑07‑27`) and optional tickers or tags.  Example:
   `2025‑07‑27_NIKE_Q3earnings.mp3`.
2. **Automatic Conversion** – On upload, a Cloud Function is triggered.  The
   function converts compressed audio to 16 kHz mono WAV using
   [`pydub`](https://github.com/jiaaro/pydub) and ensures your files are ready
   for speech recognition.  The converted file is stored alongside the
   original.
3. **Speech‑to‑Text** – The converted `.wav` file is sent to Google
   Speech‑to‑Text (v1p1beta1).  The recognizer is configured to:
   * produce word‑level time offsets and confidence scores;
   * perform automatic punctuation;
   * enable speaker diarisation with a configurable speaker count;
   * return a full JSON response.
   The raw JSON is saved in the **Transcripts/** folder with a `JSON_` prefix.
4. **Formatting** – The `pipeline/transcript_formatter.py` module reads the
   raw response and flattens the word information.  It groups contiguous words
   by speaker and minute to produce a human‑readable transcript.  Each line
   begins with a speaker label (e.g. `S1` or `S2|5`) indicating the speaker and
   minute.  The formatted transcript is saved as `<original name>.txt` in
   **Transcripts/**.
5. **Cleaning (Optional)** – If you provide an API key for Gemini or another
   large language model, the `pipeline/transcript_cleaner.py` module can use
   the raw transcript and its confidence scores to correct mis‑recognised
   words, normalise numbers and remove long silences.  This step is optional
   and configurable.
6. **Summarisation** – When a new transcript is added, a second Cloud Function
   triggers the summariser.  Using a custom prompt and your model of choice,
   `pipeline/summarizer.py` extracts key points, action items and themes.  The
   summary is stored in the **Transcripts/** folder alongside the transcript
   (e.g. `<original name>_summary.txt`).

## Folder Structure

```
Audios/             # user drop‑zone for audio files (no code lives here)
Transcripts/        # output transcripts (JSON, .txt) and summaries
pipeline/
    __init__.py     # marks this directory as a Python package
    audio_processor.py
    stt_service.py
    transcript_formatter.py
    transcript_cleaner.py
    summarizer.py
    tasks.py
    main.py         # Cloud Function entrypoint
    requirements.txt
```

### Key Files

- **audio_processor.py** – Converts audio to 16 kHz mono WAV using
  `pydub`.  It validates file types and ensures only supported audio
  extensions trigger processing.
- **stt_service.py** – Wraps Google Cloud Speech‑to‑Text.  It exposes a
  `transcribe()` function that accepts a Cloud Storage URI and returns a
  dictionary representation of the response.
- **transcript_formatter.py** – Provides `flatten_word_info()` and
  `format_transcript()` functions.  The formatter groups words by speaker
  and minute, producing labelled, readable text.  You can customise the
  diarisation labels or minute grouping here.
- **transcript_cleaner.py** – (Optional) Uses a generative model to clean
  transcripts.  This module reads environment variables for your API key and
  model name.  If no key is provided, it simply returns the original text.
- **summarizer.py** – Summarises transcripts into concise bullet points
  using your preferred model.  Prompts are stored in this module so you
  can tailor the summary style.
- **tasks.py** – Orchestrates the end‑to‑end pipeline.  It determines
  whether a new upload is an audio file or a transcript and calls the
  appropriate processors.  You can run it locally for testing or deploy
  it as a Cloud Function.
- **main.py** – Entrypoint for Cloud Functions.  Exposes an HTTP function
  and a background function that handle file uploads and dispatch tasks.

## Deployment

1. **Prepare Environment** – Ensure `ffmpeg` is available.  The
   `pydub` library relies on `ffmpeg` for audio conversion.  In Cloud
   Functions, you can include a statically linked build or use Cloud Run
   where `apt-get install ffmpeg` is permitted.
2. **Enable APIs** – Enable the Cloud Storage, Speech‑to‑Text and Cloud
   Functions APIs in your Google Cloud project.  If you plan to use
   Gemini, enable the appropriate Vertex AI or generative AI API.
3. **Create Buckets** – Create a single bucket (e.g. `dmllc`) with two
   folders: `Audios/` and `Transcripts/`.  Grant your Cloud Functions
   service account read/write permissions.
4. **Deploy Functions** – Deploy the function defined in `main.py` as a
   background Cloud Function (triggered by Cloud Storage) or as two
   separate functions for audio processing and summarisation.  Specify
   environment variables like `OUTPUT_BUCKET`, `ENABLE_CLEANING` and
   `GENAI_API_KEY` as needed.

## Error Handling & Validation

The improved pipeline includes basic validation and error handling:

* Unsupported file types are skipped with a clear log message.
* Empty or very short transcripts are detected and cleaned up.
* API errors from Speech‑to‑Text or generative models are logged and will
  propagate a retryable exception, so Cloud Functions can retry.
* Temporary files created during conversion are cleaned up to avoid
  exhausting disk space.

You can further enhance the system by adding unit tests (see `pipeline/tests/`),
tracking job status in a database (e.g. Firestore) or integrating email
notifications when summaries are ready.
