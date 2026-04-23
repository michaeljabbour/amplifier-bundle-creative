# Operator Asset Intake — Pre-Production Protocol

**Status:** Required first step of every Creative bundle project. Not optional. Skipping this costs production cycles (see `docs/PRODUCTION_LESSONS.md`).

---

## The rule

**Before any generation begins, analyze every asset the operator has supplied.**

The AI producer's default mode is to generate content based on prompts and a bias toward its own aesthetic. That is the wrong mode for existing-IP reproduction or operator-driven creative work. When the operator has *already provided* reference material, the producer's job is to **read, transcribe, and vision-analyze that material first** — and let it drive every downstream decision.

Signed: D041 (mandatory multi-modal intake), D044 (intake as first-class checklist step).

---

## The checklist

For each of the following asset types the operator supplies, perform the indicated analysis before any generation:

### Audio tracks (`.mp3`, `.wav`, `.m4a`, `.aac`, `.flac`)

1. Run OpenAI Whisper with `response_format=verbose_json`, `timestamp_granularities=[segment]`.
2. Inspect segments. **If any non-music segment contains meaningful narration, the operator's track is a narrated master, not a music bed.**
3. Save the transcript to `02_preproduction/operator_assets/audio_transcript.json`.
4. If narrated:
   - Do **NOT** synthesize TTS on top. This is D040. Direct-mux the operator's file as the single audio source.
   - Extract narration segment timestamps — these drive shot cut timing, text overlay enable ranges, and extension decisions.
5. If music-only:
   - Proceed with TTS generation per D031 (OpenAI `tts-1-hd`, cleared audio stack).
   - Duration of the track drives trailer duration per D038.

### Reference videos / mockups (`.mov`, `.mp4`)

1. Extract the audio track and run through the audio pipeline above.
2. Extract frames at 15-second intervals via ffmpeg (`ffmpeg -ss {t} -i {video} -frames:v 1`).
3. Vision-analyze each frame via `gpt-4.1-mini`: ask for `composition`, `text_visible`, `notable` (layout / camera / motion notes).
4. Save the analysis to `02_preproduction/operator_assets/mockup_analysis.json`.
5. Cross-reference with the audio transcript: each narration segment should map to one or more frames showing the operator's intended composition for that beat.

### Storyboard decks (`.pdf`, `.pptx`)

1. If PPTX, convert to PDF first (prefer operator-supplied PDF export; fall back to LibreOffice headless if unavailable).
2. Extract per-slide PNGs via `pdftoppm -png -r 110 {pdf} {outprefix}`.
3. Vision-analyze each slide: `scene`, `text_verbatim`, `characters_present`, `setting`, `book_page_hint`, `composition_note`.
4. Save to `02_preproduction/operator_assets/deck_analysis.json`.
5. Number slides map to story beats; align with narration segments.

### Existing-IP source pages (`.png`, `.jpg`, book scans)

1. Vision-extract the literal printed text of each page (D035). Save to `02_preproduction/book_text_extracted.json`.
2. Identify the font across 2+ text crops from 2+ different pages with explicit handwriting-vs-serif prompting (D037). Save to `02_preproduction/font_identification.json`.
3. Character reference selection per D028/D029 (setting-match over face-clarity-only).

### Briefs, notes, style references

1. Read them. All of them. Before any generation.
2. Summarize key constraints to `02_preproduction/brief_summary.md`.

---

## Output of intake — the operator intent map

All intake analysis rolls up into a single synthesized artifact:

```
02_preproduction/operator_intent_map.md
```

This document aligns:
- Narration timeline (from audio transcript) — when each line is spoken
- Visual flow (from mockup frames + deck slides) — what's on screen at each narration beat
- Text overlay content (from deck slides + book text extraction) — the verbatim words that appear on screen
- Character compositions (from mockup + deck) — specific staging choices the operator has made
- Source material (book pages) — what exists already vs what needs to be generated

Every downstream production script consumes this map as ground truth. Questions like "should shot 04 have the Grandfather standing or seated?" are answered by reading the map, not by asking the AI.

---

## Intake cost is trivial compared to skip cost

For a typical creative project:

| Intake step | Cost |
|---|---|
| Whisper transcription of a 5-min audio track | ~$0.002, 30 seconds |
| Vision analysis of 21 mockup frames | ~$0.05, 2 minutes parallel |
| Vision analysis of 15 PDF slides | ~$0.04, 90 seconds parallel |
| Literal book text extraction across 16 pages | ~$0.08, 90 seconds parallel |
| Multi-sample font identification | ~$0.01, 60 seconds |
| **Total intake** | **~$0.18, ~6 minutes** |

Cost of skipping intake on the pilot project project: **three full production cycles** (roughly 45 minutes of AI producer time + tens of dollars in Veo video generation that had to be reworked + extensive operator review time).

Intake is the cheapest insurance the project buys.

---

## When the operator hasn't provided assets

Ask before generating. The questions:

1. "Is there a target audio / music track? If so, where?"
2. "Is there a storyboard, mockup, or deck? Even a rough sketch is useful."
3. "Is this reproducing existing IP (a book, comic, etc.) or greenfield?"
4. "Is there a brief or style reference doc?"
5. "What's the target duration, aspect ratio, and delivery format?"

The producer should not proceed to generation until these are answered, even if the answer is "no, nothing" for some — a confirmed "nothing" is itself intake-complete for that asset type.

---

## Bundle toolkit helpers (phase 2b)

The intake protocol is supported by these helpers in the post-production toolkit:

- `whisper_transcribe(audio_path)` — returns segments + detected language + narration flag
- `extract_video_frames(video, interval_s=15)` — returns list of frame PNG paths
- `vision_analyze_frames(frames, question_schema)` — parallel vision analysis
- `pdf_to_pngs(pdf, dpi=110)` — deck extraction
- `extract_book_text(pages)` — D035 literal page text
- `identify_source_font(pages, platform="macos")` — D037 multi-sample font ID
- `build_operator_intent_map(assets)` — composes all of the above into one synthesized map

All scheduled for phase 2b. Until they ship, the pilot project project's `scripts/analyze_operator_assets.py` and `scripts/analyze_deck_slides.py` serve as reference implementations.
