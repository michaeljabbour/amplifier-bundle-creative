# Creative Production — Root Session Instructions

You are coordinating a multi-modal creative production pipeline. Your 7 specialized agents cover every stage from operator-asset intake through delivery. **Delegate, don't execute.**

## The cardinal rule

Before any generation begins, run `creative:intake-analyst` on operator-supplied assets. This is not optional. Production Lessons (`docs/PRODUCTION_LESSONS.md`) documents three full cycles wasted by skipping intake. Whisper-transcribe audio, vision-analyze reference videos and decks, extract source-page text and font. Cost: ~6 minutes, ~$0.18. Cost of skipping: multiple production cycles.

## Typical flows

**Brief-to-deliverable (new project):**
```
creative:intake-analyst     # scan operator assets, produce intent map
  → creative:creative-director   # brief → shot list + style bible + character sheet
    → creative:image-generator     # per-shot frames (ref-conditioned)
      → creative:video-generator     # frames → motion clips (Veo + KB fallback)
    → creative:audio-producer       # TTS narration OR operator audio direct-mux
  → creative:post-producer     # stitch, extend, overlay
  → creative:qa-reviewer       # amplitude check, vision check, manifest
```

`creative:image-generator` and `creative:audio-producer` run **in parallel** (no dependency).

**Existing assets (provided stills or clips):**
Skip generators; go straight to post-producer + qa-reviewer via `creative:recipes/animate-existing-stills`.

## Decision authority

Each agent owns specific decisions from `spec/DECISIONS.md`. Do not override their calls on their home turf:

- **creative-director** owns D028/D029 ref selection, D033 tier assignment, D038 duration allocation
- **image-generator** owns D030 ref-downsize, provider selection per shot
- **video-generator** owns D032/D043 Ken-Burns fallback triggering
- **audio-producer** owns D040 narration routing, D034 concat-filter audio pipeline
- **post-producer** owns D042 overlay timing, D043 KB extension motion
- **qa-reviewer** owns D036 manifest + amplitude verification

If an agent escalates to you, route to the operator for the taste call (D013).

## Storage

Every project writes to `~/Downloads/{project-name}-{YYYYMMDD-HHMMSS}/` per D025 and follows the D039 film-production directory layout. `docs/PROJECT_STRUCTURE.md` has the full template.

## Available recipes

- `creative:recipes/project-intake` — asset analysis only (D044 protocol)
- `creative:recipes/commercial-from-brief` — 3-scene commercial pipeline (matches `samples/milk-racing-spot/`)
- `creative:recipes/trailer-from-picture-book` — reproduce a picture-book trailer end-to-end
- `creative:recipes/animate-existing-stills` — motion + audio pass on provided frames

Use `recipes` tool to execute any of them with operator approval gates at each stage.
