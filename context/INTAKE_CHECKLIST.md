# Operator Asset Intake — Checklist

**Owner agent:** `creative:intake-analyst`
**Decision:** D044 — intake is the first-class first step of every project.
**Reference:** `docs/OPERATOR_ASSET_INTAKE.md` (full protocol).

Complete every applicable step before delegating to `creative-director`. Incomplete intake = cost of entire production cycle.

## Step 1 — Audio tracks (`*.mp3, *.wav, *.m4a, *.aac, *.flac`)

- [ ] Locate all audio files in `01_source/`
- [ ] Whisper-transcribe each: `response_format=verbose_json`, `timestamp_granularities=[segment]`
- [ ] Write `02_preproduction/operator_assets/audio_transcript.json`
- [ ] Scan segments: any non-music (not `♪♪`) segment with >2 words of speech ⇒ `is_narrated = true`
- [ ] Flag file as "narrated master" or "music-only" in the transcript JSON
- [ ] **If narrated** — D040 routing: agent `audio-producer` will direct-mux. Do not synthesize TTS.
- [ ] **If music-only** — proceed with TTS generation plan per D031 (OpenAI `tts-1-hd`)

## Step 2 — Reference videos / mockups (`*.mov, *.mp4`)

- [ ] Locate all video files in `01_source/`
- [ ] Extract audio, run through Step 1's audio pipeline
- [ ] Extract frames at 15-second intervals: `ffmpeg -ss {t} -i {video} -frames:v 1 {out}`
- [ ] Vision-analyze each frame via `gpt-4.1-mini`: ask for `composition`, `text_visible`, `notable`
- [ ] Write `02_preproduction/operator_assets/mockup_analysis.json`
- [ ] Cross-reference with audio transcript: each narration segment maps to one or more frames

## Step 3 — Storyboard decks (`*.pdf, *.pptx`)

- [ ] Locate all decks in `01_source/`
- [ ] If PPTX: convert to PDF (prefer operator-supplied PDF export; fall back to LibreOffice headless)
- [ ] Extract per-slide PNGs at 110 DPI: `pdftoppm -png -r 110 {pdf} {outprefix}`
- [ ] Vision-analyze each slide: `scene`, `text_verbatim`, `characters_present`, `setting`, `composition_note`, `book_page_hint`
- [ ] Write `02_preproduction/operator_assets/deck_analysis.json`
- [ ] Number slides map to story beats; verify narration-segment alignment

## Step 4 — Existing-IP source pages (`*.png, *.jpg`, book scans)

- [ ] Locate all source images in `01_source/book_pages/` (or similar)
- [ ] Per page: vision-extract literal printed text (D035)
- [ ] Write `02_preproduction/book_text_extracted.json`
- [ ] Identify the font: multi-sample vision (2+ crops from 2+ pages) with handwriting-vs-serif prompting (D037)
- [ ] Write `02_preproduction/font_identification.json`
- [ ] Character reference ranking per D029: setting-match first, face-clarity second

## Step 5 — Briefs, notes, style references

- [ ] Read every `*.md` in `01_source/`
- [ ] Summarize key constraints to `02_preproduction/brief_summary.md`

## Step 6 — Synthesize intent map

- [ ] Compose `02_preproduction/OPERATOR_INTENT_MAP.md` aligning:
    - Narration timeline (from audio transcript)
    - Visual flow (from mockup frames + deck slides)
    - Text overlay content (from deck + book text)
    - Character compositions (from mockup + deck)
    - Source material inventory (what exists vs what must be generated)

## Step 7 — Null-intake handling

If the operator supplied no assets:

- [ ] Ask the 5 questions from `docs/OPERATOR_ASSET_INTAKE.md` §"When the operator hasn't provided assets"
- [ ] Confirm each "no" answer
- [ ] Write a minimal intent map declaring `null` for each asset type

## Completion

- [ ] All applicable steps checked above
- [ ] Intent map written to `02_preproduction/OPERATOR_INTENT_MAP.md`
- [ ] Handoff to `creative-director`
