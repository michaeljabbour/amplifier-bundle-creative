# amplifier-bundle-creative

**Status:** v0.1.0 — bundle scaffolding complete. 7 agents, 5 behaviors, 4 recipes, 1 tool module (Veo 3.1 wrapper). Ready for smoke testing on a real brief.

This Amplifier bundle turns a creative brief or operator reference material into a finished multi-modal deliverable — image → video → audio → cut — with full provenance. It orchestrates OpenAI (gpt-image-2, tts-1-hd, Whisper, vision) + Google (Nano Banana Pro, Veo 3.1) + Anthropic (reasoning) + xAI (image, config-time warning) through a 7-agent pipeline, all routed through cleared providers per the D019 privacy audit.

## The pipeline

```
operator brief + assets
        │
        ▼
┌─────────────────┐
│ intake-analyst  │  (D041/D044 — Whisper, vision, PDF extraction)
└────────┬────────┘
         │ OPERATOR_INTENT_MAP.md
         ▼
┌───────────────────┐
│ creative-director │  (brief → shot list + style bible + character sheet)
└───┬───────────┬───┘
    │           │   (parallel — no dependency)
    ▼           ▼
┌──────────┐ ┌──────────────┐
│ image-   │ │ audio-       │
│ generator│ │ producer     │
└────┬─────┘ └──────┬───────┘
     │ frames/      │ tracks/
     ▼              │
┌──────────┐        │
│ video-   │        │
│ generator│        │
└────┬─────┘        │
     │ motion/      │
     ▼              ▼
┌─────────────────────┐
│    post-producer    │  (stitch + overlays + masters)
└──────────┬──────────┘
           │
           ▼
┌─────────────────┐
│   qa-reviewer   │  (amplitude + vision check, D036 manifest)
└─────────────────┘
           │
           ▼
  operator approval gate
```

## What's in this bundle

```
bundle.md                              # Root composition (thin — 22 lines)
context/                               # Shared schemas, templates, awareness pointers
  ├── creative-instructions.md         # Root session prompt
  ├── creative-awareness.md            # Thin capability map for sub-sessions
  ├── PRODUCTION_DECISIONS.md          # D019–D044 summary (agents reference this)
  ├── SHOT_SPEC_SCHEMA.md              # Shot format contract
  ├── SHOT_LIST_TEMPLATE.md            # Starter template
  ├── STYLE_BIBLE_TEMPLATE.md          # Aesthetic throughline template
  ├── CHARACTER_SHEET_TEMPLATE.md      # Character ref-ranking template
  ├── OPERATOR_INTENT_MAP_TEMPLATE.md  # Intake-analyst output synthesis
  └── INTAKE_CHECKLIST.md              # D041/D044 protocol

agents/                                # 7 specialized agents (markdown + YAML frontmatter)
  ├── intake-analyst.md                # (vision) D040/D041/D044/D037
  ├── creative-director.md             # (creative) shot list, style bible, character sheet
  ├── image-generator.md               # (fast) Nano Banana Pro + gpt-image-2
  ├── video-generator.md               # (fast) Veo 3.1 + D032/D033/D043 discipline
  ├── audio-producer.md                # (fast) TTS + direct-mux, D034 concat-filter
  ├── post-producer.md                 # (coding) ffmpeg stitching + D042/D043
  └── qa-reviewer.md                   # (critique) D036 amplitude + manifest

behaviors/                             # Reusable capability packages
  ├── full-production.yaml             # All 7 agents (bundle default)
  ├── pre-production.yaml              # intake + creative-director
  ├── shot-production.yaml             # image + video generators
  ├── audio-production.yaml            # audio-producer
  └── post-production.yaml             # post-producer + qa-reviewer

recipes/                               # Orchestration workflows
  ├── project-intake.yaml              # (163 lines, 3 stages, 1 approval)
  ├── commercial-from-brief.yaml       # (472 lines, 7 stages, 3 approvals)
  ├── trailer-from-picture-book.yaml   # (508 lines, 7 stages, 4 approvals)
  └── animate-existing-stills.yaml     # (447 lines, 6 stages, 2 approvals)

modules/tool-video/                    # In-bundle Amplifier tool module
  ├── amplifier_module_tool_video/
  │   ├── __init__.py                  # mount() — registers generate_video + list_video_models
  │   ├── provider.py                  # google-genai SDK wrapper
  │   ├── schemas.py                   # Pydantic input schemas
  │   └── validation.py                # D033 tier × duration matrix + typed exceptions
  ├── tests/test_validation.py         # 54 unit tests (no API calls)
  └── pyproject.toml                   # Extracts to separate repo when other bundles need it

spec/                                  # Design artifacts
  ├── SPEC.md                          # Frozen design baseline
  └── DECISIONS.md                     # 41 resolved decisions (forensic log)

docs/                                  # Reference material
  ├── PRODUCTION_LESSONS.md            # Two reference cycles — what worked, what broke
  ├── PROJECT_STRUCTURE.md             # D039 directory convention (every project follows)
  ├── OPERATOR_ASSET_INTAKE.md         # D041/D044 full checklist
  └── api-privacy-comparison.md        # D019 provider audit

samples/                               # Reference output
  └── milk-racing-spot/                # Hand-rolled 27s commercial (pre-bundle era, kept for comparison)
```

## Quick start

```bash
# Load the bundle (once its package is installed or checked out)
amplifier bundle load creative

# Run any of the 4 recipes
amplifier run creative:recipes/commercial-from-brief \
    project_name=acme-hero-spot \
    brief_path=./brief.md \
    target_duration_s=30 \
    narration_voice=onyx

# Recipe will pause at 3 approval gates (creative direction → frames → master)
# Output master lands at ~/Downloads/acme-hero-spot-YYYYMMDD-HHMMSS/06_masters/v1_titled.mp4
```

## The 4 recipes — when to use which

| Recipe | Inputs | When to use |
|---|---|---|
| `project-intake` | Operator assets in `source_dir/` | Wait-and-see pass: let the producer analyze everything and report back before committing to full production |
| `commercial-from-brief` | Verbal brief | Greenfield campaign work — 15–45 s commercial from a creative ask |
| `trailer-from-picture-book` | Book pages + optional narration | Existing-IP trailer/animation work (exercises D028/D029 ref-image-first) |
| `animate-existing-stills` | Approved stills + optional VO/music | Image-campaign → motion extension (skip generation, just motion + audio + master) |

All recipes pause at approval gates (creative direction, frames, master) so the operator can course-correct before each downstream stage. Per D013, operators win taste calls; agents win hard-rule calls (refs present, tier validity, amplitude at anchors, budget).

## Decisions owned by each agent

| Agent | Decisions they own at call time |
|---|---|
| intake-analyst | D037 (multi-sample font ID), D040 (narration routing), D041 (multi-modal intake), D044 (intake-first) |
| creative-director | Shot decomposition, D028 ref-page selection, D029 setting-match heuristic, D033 tier×duration, D035 text overlay mapping, D038 music-driven duration |
| image-generator | D028/D029 ref-first conditioning, D030 ref-downsize, provider selection per shot |
| video-generator | D033 tier validation, D032 KB fallback on quota exhaustion |
| audio-producer | D031 TTS voice selection, D034 concat-filter pattern, D038 music-driven duration, D040 direct-mux routing |
| post-producer | D042 narration-synced overlays, D043 KB on held extensions, D035 verbatim text |
| qa-reviewer | D036 amplitude verification + manifest authorship, D013 taste-vs-hard-rule boundary |

Full decision log: `spec/DECISIONS.md` (41 resolved entries with forensic trigger/resolution each).

## Storage convention

Every project writes to `~/Downloads/{project-name}-{YYYYMMDD-HHMMSS}/` per D025, following the D039 film-production layout. See `docs/PROJECT_STRUCTURE.md` for the full template — `01_source/` through `99_archive/` with numeric prefixes that enforce the pre-production → shot-production → audio → post → delivery flow.

## The reference sample

`samples/milk-racing-spot/` contains a 27-second commercial (3 scenes: pit-stop hand-off → hero pour → podium spray) that was **hand-rolled before this bundle existed**. It's kept in the repo for comparison: `v2_commercial.mp4` is the human-scripted output; once the bundle is smoke-tested against the same brief, a `v3_via_bundle.mp4` will join it so readers can compare hand-rolled vs bundle-orchestrated output.

## Dependencies

| Dependency | Role | Status |
|---|---|---|
| [`amplifier-foundation`](https://github.com/microsoft/amplifier-foundation) | Base tools + session + hooks | Composed via `bundle.md` |
| [`amplifier-bundle-recipes`](https://github.com/microsoft/amplifier-bundle-recipes) | Recipe orchestration | Composed via `bundle.md` |
| [`amplifier-bundle-imagen`](https://github.com/michaeljabbour/amplifier-bundle-imagen) | Visual Director specialist agents | Composed via `behaviors/full-production.yaml` + `behaviors/shot-production.yaml` |
| [`imagen-mcp`](https://github.com/michaeljabbour/imagen-mcp) | Image-generation MCP server | Wrapped by `amplifier-bundle-imagen` |
| `modules/tool-video` (in-bundle) | Veo 3.1 wrapper as Amplifier tool module | In-bundle for now; extracts when other bundles need it |

## Roadmap

- **Phase 0** — Design baseline ✓
- **Phase 1** — Reference productions + lessons capture ✓
- **Phase 2a** — Bundle scaffolding ✓ *(this release)*
  - `bundle.md`, context/, agents/, behaviors/, recipes/, modules/tool-video/
  - 4 recipes: project-intake, commercial-from-brief, trailer-from-picture-book, animate-existing-stills
- **Phase 2b** — Smoke testing + post-production toolkit helpers
  - Reproduce milk-racing-spot via `amplifier run creative:recipes/commercial-from-brief`
  - Extract `modules/tool-video` to its own repo once another bundle needs it
  - Add `whisper_transcribe`, `build_operator_intent_map`, `extend_via_held_frame` as module-level helpers
- **Phase 2c** — Second reference project through the bundle (catch v4.1-style gaps)
- **Phase 3** — Public beta + docs polish

## Using this

- Read `spec/SPEC.md` for the frozen design baseline.
- Read `docs/PRODUCTION_LESSONS.md` for the narrative of two reference cycles — what broke, what changed, why agents are shaped the way they are.
- Read the last ~10 entries in `spec/DECISIONS.md` for the most recent rulings.
- Read the agent you're about to invoke (`agents/<name>.md`) before building instructions for it — the `description` field tells you *when* to invoke, the body tells you *how the agent thinks*.
- Read `docs/OPERATOR_ASSET_INTAKE.md` before starting any project where the operator has provided reference material.

## Contributing

Bundle work during v0.1 is happening on `main` directly — no branches, fast iteration. New decisions append to `spec/DECISIONS.md` with a full body entry. New production narratives append to `docs/PRODUCTION_LESSONS.md`. Both files are append-only; never rewrite history.

Agent edits go in `agents/<name>.md`; behavior composition edits go in `behaviors/<name>.yaml`; recipe edits via the `recipes:recipe-author` agent.
