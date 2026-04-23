# Creative Production Capability

This session has access to a 7-agent creative production pipeline for multi-modal deliverables (book trailers, commercials, marketing assets).

## When to delegate

| Agent | Use for |
|---|---|
| `creative:intake-analyst` | Operator-supplied audio, video mockups, PDF/PPTX decks, source IP (MANDATORY first step) |
| `creative:creative-director` | Brief → shot list + style bible + character sheet (ALWAYS after intake) |
| `creative:image-generator` | Per-shot image generation with ref-conditioning |
| `creative:video-generator` | Frame-to-motion via Veo 3.1 with Ken-Burns fallback |
| `creative:audio-producer` | TTS narration OR operator-audio direct-mux |
| `creative:post-producer` | ffmpeg stitching, held-frame KB extensions, narration-synced overlays |
| `creative:qa-reviewer` | Vision QA per shot, amplitude check on audio anchors, production manifest |

## Critical protocols

- **Intake first, always** — D041/D044. Skipping it costs production cycles.
- **Storage** — `~/Downloads/{project}-{timestamp}/` per D025, D039 layout.
- **Ref-image-first** — D028 for existing-IP projects; D029 for setting-match selection.
- **Concat-filter audio** — D034. Never `amix`, never `apad`, never single-pass `loudnorm`.
- **Ken-Burns on held extensions** — D043. Static holds are prohibited.
