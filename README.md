# DMLLC

### 📂 Structure
### 🧠 Features

- Auto-transcribes  or  files uploaded to 
- Uses **Google Speech-to-Text v2** (with punctuation + speaker diarization)
- Outputs formatted text to 
- Everything is Dockerized and deployable to Cloud Run
- Includes formatting utilities




# DMLLC

###🎵 Audios

• User drops an .mp3 or .wav audio file into the audios/ folder in Google Cloud Storage.
• This upload automatically triggers the pipeline.
• Audio .mp3 files are converted to .wav files for processing
• Converted audio files are sent to transcription phase 1

⸻

##🏁 Transcription

###🏎️ Raw Transcription

• Google Speech-to-Text v2 API is used with punctuation and speaker diarization enabled.
• Transcription results are returned in structured JSON format with confidense levels.
• Transcripts are saved in the Transcripts/ folder.
• Converted audio files are sent to transcription phase 2

###⛵ Clean Transcription

• Gemini 2.5 uses confidense levels and context to clean up words/phrasing throughout transcript
• A post-processing script formats transcripts into clean, readable text.
• Speaker turns are labeled, punctuation is finalized.
• Long silences/irrelevant segments may be removed/merged.
• Transcripts are saved in the DMLLC/Transcripts/ folder.

⸻

###✈️ Summarize

• Trigger call pulls transript when added to folder
• A summarization script produces an overview of the call or meeting.
• Key themes or highlights are extracted based on custom Gemini 2.5 prompts.
• Output summaries are saved in the DMLLC/Summaries/ folder.
