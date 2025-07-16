# DMLLC Mtg Pipeline

### 🏁 Audios

- User drops an .mp3 or .wav audio file into the audios/ folder in Google Cloud Storage.
- This upload automatically triggers the pipeline.
- Audio .mp3 files are converted to .wav files for processing
- Converted audio files are sent to transcription phase 1

### 🏎️ Raw Transcription

- Uses **Google Speech-to-Text v2** (with punctuation + speaker diarization enabled)
- Transcription results are returned in structured JSON format with confidense levels.
- Transcripts are saved in the Transcripts/ folder.
- Converted audio files are sent to transcription phase 2

### ⛵ Clean Transcription

- Gemini 2.5 uses confidense levels and context to clean up words/phrasing throughout transcript
- A post-processing script formats transcripts into clean, readable text.
- Speaker turns are labeled, punctuation is finalized.
- Long silences/irrelevant segments may be removed/merged.
- Transcripts are saved in the DMLLC/Transcripts/ folder.

### ✈️ Summarize

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
- Matched html text is pushed to site in new section
- Each section uses relevant html formatting to upload each type to correct spot
