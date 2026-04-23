# amplifier-bundle-creative

**Status:** Design-v0.1 (see `spec/SPEC.md`), **validated through one real end-to-end production** (the pilot project picture-book animation, 4 iterations). 41 resolved decisions on file. Phase 2a implementation starts next.

The bundle itself (agents, behaviors, MCPs, coordination-file Context module) still hasn't landed — but the spec is no longer theoretical. The first reference project revealed five distinct failure modes and five new corrective decisions, all captured in `spec/DECISIONS.md`. Every design assumption the bundle makes is now either confirmed by successful production use or revised based on what actually broke.

---

## What this is

A planned Amplifier bundle that turns a creative brief into a reviewable deliverable with a full provenance trail, by orchestrating:

- **Image generation** — OpenAI gpt-image-2, Google Nano Banana 2/Pro; Ideogram / Recraft / Flux permanently removed per the D019 privacy audit
- **Video generation** — Google Veo 3.1 (Lite / Fast / Standard); xAI Grok Imagine Video cleared with config-time warning; Sora 2 stubbed only (deprecating 2026-09-24)
- **Audio** — operator-supplied tracks direct-muxed (D040); OpenAI `tts-1-hd` for narration-synthesis when needed (D031); ElevenLabs Enterprise reserved for v0.2 AudioGeneration surface (D022)
- **Creative critique** — vision-LLM-based via Amplifier's routing matrix (Claude Opus, GPT-4.1, Gemini 3 Pro vision)

All providers passed the D019 privacy audit or were permanently removed. See `spec/SPEC.md` for the frozen v0.1 design and `spec/DECISIONS.md` (41 entries) for the rolling resolutions log.

---

## The reference project — pilot project

The first full production cycle took a 16-page children's picture book to a 5:15 animated trailer with 32 shots, narration-synced text overlays, music bed, opening question card, and title card. Four iterations (v1 → v4.1) with operator review between each. The run directory (in `~/Downloads/`, per D025) is organized as a film production per D039 — the layout is documented in `docs/PROJECT_STRUCTURE.md` as the canonical pattern for future Creative bundle projects.

Production details, artifacts, and the operator intent map live in that run directory. What came back to the bundle is lessons (`docs/PRODUCTION_LESSONS.md`) and the formal decisions log — these are the deliverables from the reference project as far as the bundle repo is concerned.

### What the reference project validated

- **Reference-image-first generation** (D028) held up: every shot of the pilot-project trailer was conditioned on the operator's actual source illustrations via Nano Banana Pro. Character-identity drift stayed at zero across 32 shots.
- **Setting-match reference selection** (D029) beat face-clarity-optimal ref selection. Shot 1's v2 candidate (landscape refs) read more correctly than v3 (face-clarity refs from non-matching settings).
- **File-to-Downloads storage discipline** (D025): the operator navigated all four versions' artifacts naturally without any ceremony. The film-production directory structure (D039) made the 149-file run dir navigable.
- **Ken-Burns quota fallback** (D032): when Veo 3.1 quota exhausted mid-run, shots with correct frames got subtle-zoom fallback motion and shipped. Operator accepted the trade — character fidelity preserved, motion degraded gracefully.
- **Ruthless cleared-provider stack**: OpenAI + Google + Anthropic + xAI (four providers) covered every capability the project needed. No pressure to revisit the permanently-removed BFL/Ideogram/Recraft/ElevenLabs-aggregator.

### What the reference project changed

Five new decisions landed as a direct result of what broke:

- **D040** — operator-provided audio supersedes synthesized narration. Whisper-transcribe before generating TTS. The bundle was stacking TTS on top of operator-provided narrated tracks.
- **D041** — multi-modal operator reference intake is mandatory. Look at the operator's mockup video / deck / PPTX before generating anything. The operator had an entire 40s opening sequence the AI producer ignored for three cycles.
- **D042** — text overlays must be timed to narration segments, not shot cuts. Use Whisper segment timestamps to drive overlay enable ranges.
- **D043** — held-frame extensions must carry Ken-Burns motion. Static held-frames are read as scene-transition gaps.
- **D044** — asset intake becomes a first-class checklist step. Not a sub-bullet, not an "if time permits" — the first thing pre-production does is look at what the operator already provided.

Full narrative in `docs/PRODUCTION_LESSONS.md`. The new pre-production protocol is documented in `docs/OPERATOR_ASSET_INTAKE.md`.

---

## Repo map

```
amplifier-bundle-creative/
├── README.md                          (this file)
├── spec/
│   ├── SPEC.md                        (frozen design-v0.1 — (frozen design baseline))
│   └── DECISIONS.md                   (rolling log — 41 resolved entries)
├── docs/
│   ├── PROJECT_STRUCTURE.md           (D039 — film-production folder layout every project follows)
│   ├── OPERATOR_ASSET_INTAKE.md       (D041/D044 — mandatory pre-production analysis protocol)
│   ├── PRODUCTION_LESSONS.md          (rolling narrative — v2 and v4/v4.1 cycles so far)
│   ├── api-privacy-comparison.md      (D019 — the privacy audit that cleared the provider stack)
│   └── api-privacy-comparison.html    (same, rendered)
```

No `modules/`, `agents/`, `behaviors/`, or `recipes/` directory yet. Phase 2a lands those.

---

## Relationship to other repos

| Repo | Role | Status |
|---|---|---|
| [`imagen-mcp`](https://github.com/michaeljabbour/imagen-mcp) | Image-generation MCP server | Shipping (v0.3.0). Will be extended in Phase 2a with Nano Banana Pro ref-image downsize (D030) + bundle-toolkit helpers (from production lessons). |
| [`amplifier-bundle-imagen`](https://github.com/michaeljabbour/amplifier-bundle-imagen) | Image-focused bundle (Visual Director specialists) | Shipping (v1.1.0). Will be composed as a sub-behavior of this bundle in Phase 2b. |
| `video-mcp` (new) | Async video-generation MCP server | Phase 2a. Shot-spec validation against per-tier Veo duration constraints (D033) lands in v0.1.1. |
| `amplifier-bundle-creative` (this repo) | Orchestration bundle composing imagen-mcp + video-mcp + AudioGeneration | Design validated via pilot project reference project; code scaffolding begins Phase 2a. |

---

## Roadmap

### Phase 0 — Design checkpoint (done)
- `spec/SPEC.md` frozen at `design-v0.1`
- Privacy audit (D019) complete; four cleared providers + permanent removals
- Reference project (pilot-project trailer) validated 41 decisions across v1→v4.1 cycles

### Phase 1 — Design refinements from reference project (done)
- D028–D044 (17 new decisions) captured
- `docs/PROJECT_STRUCTURE.md`, `docs/OPERATOR_ASSET_INTAKE.md`, `docs/PRODUCTION_LESSONS.md` shipped

### Phase 2a — Bundle scaffolding (next)
- `video-mcp` v0.1 with Veo 3.1 + per-tier duration validation (D033)
- `imagen-mcp` v0.4 with ref-downsize helper baked in (D030)
- Bundle skeleton: `bundle.yaml`, `agents/`, `behaviors/`, `context/` directories
- Project-intake checklist agent that runs the D044 protocol automatically

### Phase 2b — Post-production toolkit
- `produce_vo_track`, `mix_music_vo`, `extend_via_held_frame` (with KB default per D043), `render_narration_synced_overlays` (D042), `verify_audio_audible_at` (D036), `identify_source_font` (D037), `whisper_transcribe`, `vision_analyze_frames`, `pdf_to_pngs`, `build_operator_intent_map` (D041/D044)
- `init_project_dir(name, output_root)` — creates the D039 layout with placeholder READMEs

### Phase 2c — Second reference project
- Run the bundle (not hand-rolled scripts) on a new brief end-to-end
- Catch whatever v4.1-style gaps this architecture hasn't yet surfaced
- Cycle updates back into DECISIONS.md and PRODUCTION_LESSONS.md

### Phase 3 — Public beta
- Docs, examples, `amplifier-bundle-imagen` re-composition
- Recipe layer (if the orchestration pattern calls for one)

---

## How to read the decisions log

`spec/DECISIONS.md` is append-only. Each entry has:
- **Index table row** at the top: ID, summary, status
- **Body entry** further down: status, spec section, trigger (what made this surface), resolution, implementation landing, who decided

Entries are grouped by date of resolution. New decisions get added to the most recent date section (or start a new one for a new production cycle). Once resolved, a decision is not edited — if reality changes, a new decision supersedes it and the old entry is annotated with a pointer to the superseder. This is so the log stays forensic: any future reader can reconstruct what we believed at any point, why, and what made it change.

See `docs/PRODUCTION_LESSONS.md` for the narrative arc across decisions — it's the "why" that the DECISIONS entries compress into their "trigger" fields.

---

## Contributing / operating

The bundle isn't code yet. For now, the repository exists to version the design and capture the decisions. If you're running the design process as the operator:

1. Read `spec/SPEC.md` for the frozen v0.1 design.
2. Read the latest `docs/PRODUCTION_LESSONS.md` section to see what the last cycle learned.
3. Read the last ~5 entries in `spec/DECISIONS.md` — those are the most likely to affect your current work.
4. If you're starting a new creative project with this bundle's approach, open `docs/OPERATOR_ASSET_INTAKE.md` and run the checklist before any generation.

If you're contributing back: any new decision goes in `spec/DECISIONS.md` with an index row + full body entry following the template of the existing entries. Production narrative and lessons go in `docs/PRODUCTION_LESSONS.md`. Both files are append-only; never rewrite history.
