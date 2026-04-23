# Sample Production — "Fuel the Fastest"

A three-scene hero-still campaign demonstrating how this bundle handles a greenfield (no-existing-IP) creative brief.

**Brief:** 30-second sponsorship commercial where a milk board backs a motorsport team. Milk is reframed as performance fuel. Three scenes: approach → hero pour → victory.

**Campaign line:** *Fuel the fastest.*

**Output format:** three 16:9 photorealistic commercial stills, usable as standalone print/social assets OR as first-frame conditioning for Veo 3.1 motion clips in a later pass.

## Quick look

| # | Frame | Role |
|---|-------|------|
| 1 | `03_shots/shot_01_approach.png` | Setup — race car in the pit, crew member offers a cold bottle of milk |
| 2 | `03_shots/shot_02_hero_pour.png` | Hero — extreme-macro beauty shot of the pour |
| 3 | `03_shots/shot_03_victory.png` | Payoff — podium, driver sprays milk like champagne |

## What this sample demonstrates

This is a **clean-sheet** sample: no operator-supplied reference mockup, no existing IP to reproduce. It exercises the bundle's protocols for a verbal-brief-only input:

- **Film-production directory layout (D039)** — every project written with this bundle follows the `0N_stage/` numbered prefix convention. This sample uses an abbreviated layout (only `01_brief`, `02_preproduction`, `03_shots`, `08_qa`) because it's stills-only and has no operator assets / audio / logs / titles.
- **Skip D040 and D041** — intake protocol applies *when the operator supplies reference material*. There's no operator audio to transcribe and no mockup to vision-analyze here, so the intake step trivially exits. The producer goes straight to creative brief → shot list → generation.
- **Aesthetic throughline (STYLE_BIBLE.md)** — three shots share a locked palette and lighting doctrine so they read as one campaign.
- **Cleared-provider stack (D019)** — generation is Gemini Nano Banana Pro throughout, auto-selected for photorealistic commercial imagery with no text-heavy elements. No BFL / Ideogram / Recraft / etc.
- **QA manifest (D036)** — `08_qa/production_manifest.json` records provider, model, resolution, timing, and selection rationale for every shot. Any reviewer can reconstruct what was run.

## What this sample does NOT demonstrate

(Each of these is a bundle capability the Giving-Mind-style reference project in `docs/PRODUCTION_LESSONS.md` covers instead.)

- **Multi-modal operator intake** (D041) — no mockup video, PDF deck, or audio track here
- **Whisper narration extraction** (D040) — no audio
- **Reference-image-first generation** (D028/D029) — no source IP to reproduce
- **Held-frame Ken-Burns extensions** (D043) — no video timeline
- **Narration-synced text overlays** (D042) — no narration track
- **Veo 3.1 motion generation** — these are stills; frames are ready to feed Veo as first-frame conditioning, but no motion pass was run

## Repro steps

The generation calls this sample ran are:

```python
# Scene 1 — Approach (pit stop hand-off)
mcp_imagegen.generate_image(
    prompt="<see 02_preproduction/SHOT_LIST.md Shot 01>",
    provider="gemini",
    gemini_model="nano-banana-pro",
    aspect_ratio="16:9",
    size="2K",
    output_path="03_shots/shot_01_approach.png",
)

# Scene 2 — Hero pour (extreme macro)
mcp_imagegen.generate_image(
    prompt="<see 02_preproduction/SHOT_LIST.md Shot 02>",
    provider="gemini",
    gemini_model="nano-banana-pro",
    aspect_ratio="16:9",
    size="2K",
    output_path="03_shots/shot_02_hero_pour.png",
)

# Scene 3 — Victory (podium milk spray)
mcp_imagegen.generate_image(
    prompt="<see 02_preproduction/SHOT_LIST.md Shot 03>",
    provider="gemini",
    gemini_model="nano-banana-pro",
    aspect_ratio="16:9",
    size="2K",
    output_path="03_shots/shot_03_victory.png",
)
```

All three shots: one pass each, no regeneration, ~85 s total wall-clock via `imagegen` MCP.

## Directory layout

```
samples/milk-racing-spot/
├── README.md                          (this file)
├── 01_brief/
│   └── CREATIVE_BRIEF.md              (campaign concept + 3-scene arc)
├── 02_preproduction/
│   ├── SHOT_LIST.md                   (per-shot composition + prompt intent)
│   └── STYLE_BIBLE.md                 (aesthetic throughline — palette, light, lens language)
├── 03_shots/
│   ├── shot_01_approach.png
│   ├── shot_02_hero_pour.png
│   └── shot_03_victory.png
└── 08_qa/
    └── production_manifest.json       (provider, model, timing, selection rationale per shot)
```

## Extending this sample

Natural next steps if you wanted to extend this into a 30-second commercial:

1. **Motion pass** — each shot's PNG is first-frame-conditioning for a Veo 3.1 clip (6–8 s each at Fast or Standard tier). Keep the frame, animate the subtle motion — tire smoke drift for Shot 01, the splash crown hitting the bottle for Shot 02, the crowd's cheer for Shot 03.
2. **Audio** — either original score + VO via OpenAI `tts-1-hd`, or operator-supplied track following D040.
3. **Finishing** — tagline lockup ("FUEL THE FASTEST") added via text-overlay pass; narration-synced per D042 if voice is added.

The bundle's protocols scale from this stills-only sample up to the full ~5-minute reference project described in `docs/PRODUCTION_LESSONS.md`.
