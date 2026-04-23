# Production Decisions — Quick Reference Card

One-paragraph summaries of the decisions from `spec/DECISIONS.md` that agents need at call time. For full rationale, trigger, and implementation-landing details, consult `spec/DECISIONS.md` in the bundle root.

---

## Provider stack

**D019** — Cleared provider set: OpenAI (image, TTS, Whisper, vision), Google (Nano Banana Pro + Veo 3.1), Anthropic (reasoning), xAI Grok (image with config-time warning). Permanently removed: BFL Flux, Ideogram, Recraft, ElevenLabs aggregator. Do not propose or integrate anything outside this list.

**D021** — Provider selection lives inside the MCP, not at the agent layer. Agents describe capability needs; MCPs dispatch to the right provider.

**D031** — OpenAI `tts-1-hd` is the v0.1 narration voice. Default: `voice=fable`, `speed=0.92`. For confident sports/commercial register use `voice=onyx`. ElevenLabs remains v0.2 scope per D022; do not layer TTS on top of operator-provided narration (see D040).

## Storage + structure

**D025** — All artifacts write to `~/Downloads/{project-name}-{YYYYMMDD-HHMMSS}/`. No other path. Operator navigates via Finder without ceremony.

**D039** — Every project follows the film-production directory layout: `01_source/`, `02_preproduction/`, `03_shots/`, `04_audio/`, `05_titles/`, `06_masters/`, `07_logs/`, `08_qa/`, `99_archive/`, `scripts/`. See `docs/PROJECT_STRUCTURE.md` for the full template.

## Reference-image discipline

**D028** — For existing-IP (book pages, approved character refs), every generation is reference-conditioned. Text-only prompts fail character-identity checks within 2-3 shots.

**D029** — Reference selection optimizes for setting-match first, face-clarity second. A ref with the correct lighting/environment + imperfect face beats a face-perfect ref in the wrong setting.

**D030** — Downsize reference images to ≤1400px longest edge before sending to Nano Banana Pro. ImageMagick: `convert {src} -resize 1400x1400\> -quality 95 {dst}`.

## Video generation

**D033** — Veo 3.1 tier×duration matrix: `lite` supports 4-6s only; `fast` and `standard` support 8s. Validate before submit; auto-downgrade `fast@6s` → `lite@6s`.

**D032** — On Veo 429 RESOURCE_EXHAUSTED after retry window: ambient/transitional shots fall back to Ken-Burns on the approved frame; character-critical/final-deliverable shots wait for quota, never Ken-Burns.

**D043** — Held-frame extensions must use Ken-Burns zoom (`zoompan z='min(zoom+0.0006,1.04)'`), never static. Verify via frame-hash at two points inside the hold — identical hashes = static = failure.

## Audio

**D034** — Audio tracks are built via `concat` filter. Segment pattern: `silence → vo → silence → vo → ...`, each segment `aformat=sample_rates=44100:channel_layouts=stereo`, joined with `concat=n=N:v=0:a=1`. **NEVER** use `amix`, `apad`, or single-pass `loudnorm` — all three were proven to produce silent masters in production.

**D038** — Music duration drives animation duration. If operator supplies a music track, target length = music length. Visuals fit music, not the reverse.

**D040** — If operator-supplied audio contains narration (detected via Whisper transcript — any non-music segment with meaningful speech), that audio **is** the master track. Direct-mux it. Do not synthesize TTS on top. Stacked narration was the v3 bug on the pilot project.

**D042** — Text overlays time to Whisper narration-segment boundaries, not to shot cuts. Overlay `enable='between(t, narration_start - 0.3, narration_end + 1.0)'`. Silent music passages = no text on screen.

## Intake protocol

**D041** — Operator-supplied reference material (video mockups, decks, source pages, audio) is vision-analyzed before any generation. Mockups → frame extraction + vision analysis. Decks → PDF → per-slide vision. Source pages → literal text extraction + font identification.

**D044** — Intake is the first-class first step of every project. Before character sheets, before shot lists, before generation. See `docs/OPERATOR_ASSET_INTAKE.md` for the full checklist.

## QA

**D036** — The production manifest is authoritative for what was generated, with what settings, via which provider/model/tier. Amplitude-check audio at every VO anchor timestamp (peak > 500 on 16-bit signed, non-zero ratio > 10%). Don't trust `ffprobe` alone — an audio stream can be present and completely silent.

**D037** — Font identification uses multi-sample vision (2+ text crops from 2+ different source pages) with explicit handwriting-vs-serif prompting. Single-sample font guessing was wrong 50% of the time in production.

## Operator approval

**D013** — On taste calls (does this look right? does this land?), the operator wins. Agents are authoritative on hard rules (refs present, D033 tier validity, amplitude at anchors, budget limits) but never on aesthetic judgment.

---

*Additions go in `spec/DECISIONS.md` with forensic trigger/resolution. Summaries here follow.*
