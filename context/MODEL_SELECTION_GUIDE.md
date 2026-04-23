# Model Selection Guide — How the Producer Executes Its Vision

Right model for the right task. Agents reference this at decision time.

Four axes: **reasoning depth**, **image provider**, **video tier**, **voice register**. Each maps to a concrete cost and quality profile. Over-reaching on any axis wastes budget without improving the deliverable; under-reaching sacrifices quality where it matters.

---

## Axis 1 — Agent `model_role` assignments

Declared in each agent's frontmatter. Fallback chain goes specific → general. The routing matrix resolves `model_role` to a concrete provider/model per active matrix.

| Agent | `model_role` | Why |
|---|---|---|
| `intake-analyst` | `[vision, fast, general]` | Primary work is seeing (mockup frames, deck slides, source pages, fonts). Secondary is fast transcription/extraction. Vision-native model is non-negotiable. |
| `creative-director` | `[creative, reasoning, general]` | Translates brief + intent map into shot list. Needs aesthetic judgment (creative) and multi-step planning (reasoning: D033 tier math, D038 duration allocation, D043 extensions). Deepest reasoning budget in the bundle. |
| `image-generator` | `[fast, general]` | Decides provider + prompts per shot, but doesn't make aesthetic calls — the director already did. Fast is sufficient. |
| `video-generator` | `[fast, general]` | Routes between Veo tiers + Ken-Burns fallback. Mechanical decisions, not creative ones. Fast. |
| `audio-producer` | `[fast, general]` | Routes narration vs. direct-mux, picks voice, builds concat-filter VO track. Fast. |
| `post-producer` | `[coding, fast, general]` | Writes and executes ffmpeg filter chains. Coding-oriented model with fast fallback for the simpler compositing work. |
| `qa-reviewer` | `[critique, vision, general]` | Vision-checks frames vs refs, finds what's wrong. Critique model spots issues generative models miss. Vision fallback covers the pure-visual comparisons. |

Premium reasoning is reserved for `creative-director` alone. Everyone else works off the director's plan — no need to re-think the deliverable at every step.

---

## Axis 2 — Image provider selection

Cleared stack per D019: **OpenAI gpt-image-2** and **Google Nano Banana Pro**. No others.

### Decision matrix (image-generator owns this call)

| Shot characteristic | Choose | Why |
|---|---|---|
| Reference-image-first (existing IP, character continuity) | **Nano Banana Pro** | Multi-ref conditioning up to 14 images; respects setting-match ranking (D029); survives character identity across 30+ shots. |
| Photorealistic product or portrait, no text | **Nano Banana Pro** | Produces the cleanest commercial photography. |
| 2K or 4K output required | **Nano Banana Pro** | gpt-image-2 is capped at 1536×1024 widescreen. |
| Text in the image (menus, infographics, title-card typography, mockup UI copy) | **OpenAI gpt-image-2** | 99% text accuracy; Nano Banana can't reliably render non-trivial copy. |
| Logos, specific brand marks, typographic layouts | **OpenAI gpt-image-2** | Same reasoning — text discipline. |
| Transparent background needed (PNG alpha) | **OpenAI gpt-image-2** | Supports `background=transparent`; Nano Banana does not. |
| Iterative multi-turn refinement with conversation memory | **OpenAI gpt-image-2** | Responses API conversation threads preserve context across calls. |
| Real-time data (weather, stock prices, live events rendered into the image) | **Nano Banana Pro** | Only provider with Google Search grounding. |

### Shot-type shortcuts

- **Character-on-setting refs, photoreal illustration** → Nano Banana Pro, `4 refs minimum`
- **Hero product beauty macro, no copy** → Nano Banana Pro, 2K
- **Title card with credits typography** → OpenAI gpt-image-2, 1024×1536 portrait or 1536×1024 landscape
- **Opening question card with 4 lines of copy in a specific font** → OpenAI gpt-image-2
- **Emotional close-up, golden-hour register** → Nano Banana Pro
- **Infographic with labeled diagram** → OpenAI gpt-image-2
- **Abstract gradient background plate** → either; default to Nano Banana Pro for quality, switch to gpt-image-2 on quota pressure

### Reference-image rules (D028, D029, D030)

- **D028** — existing-IP work is always ref-conditioned. Text-only prompts for a named character drift within 2-3 shots.
- **D029** — rank refs by setting-match first, face-clarity second. A face-medium ref in the correct setting beats a face-perfect ref in the wrong setting.
- **D030** — downsize refs to ≤1400px longest edge before sending to Nano Banana Pro. ImageMagick: `convert {src} -resize 1400x1400\> -quality 95 {dst}`. Over-large refs have produced silent failures in production.

---

## Axis 3 — Video tier selection (Veo 3.1)

`modules/tool-video` exposes three tiers. Pick the lowest tier that clears the shot's bar.

### D033 validity matrix (hard constraint — enforced at submit time)

| Tier | Allowed durations | Resolution | Cost tier | Strength |
|---|---|---|---|---|
| `lite` | 4, 5, 6 seconds | 1080p | $ | Short ambient/transitional beats, cutaways, coda shots. |
| `fast` | 8 seconds | 1080p | $$ | Standard 8s motion shots where character identity isn't story-critical. |
| `standard` | 8 seconds | 1080p | $$$ | Hero beats, character-critical motion, story-critical action (hand-offs, reveals). |

Invalid (tier, duration) pairs raise `VeoTierMismatch` before API submit. `fast@6s` auto-downgrades to `lite@6s`.

### Shot-tag → tier routing (creative-director assigns; video-generator executes)

| Shot tag | Default tier | When to upgrade |
|---|---|---|
| `ambient-transitional` | `lite` (4-6s) | Never. Ken-Burns fallback is also acceptable for these on quota pressure. |
| `hero-beat` | `fast` (8s) | Upgrade to `standard` if the shot's punchline depends on a specific motion landing (e.g., a hand-off, a pour, a spray arc). |
| `final-deliverable` | `standard` (8s) | No downgrade. Title cards and end cards may use `lite` if pure-typographic, but if there's motion in frame, standard. |
| `character-critical` | `standard` (8s) | No downgrade under any condition. **Never Ken-Burns fallback** — wait for quota. |

### Ken-Burns fallback (D032, D043)

- **Triggered by**: sustained `VeoQuotaExhausted` after 30s/60s/120s retry backoff.
- **Allowed for**: `ambient-transitional` only.
- **Forbidden for**: `character-critical`. Wait for quota, never substitute.
- **Never static**: held-frame extensions always carry subtle Ken-Burns zoom (`zoompan=z='min(zoom+0.0006,1.04)'`). Verify via frame-hash at two timestamps within the hold — identical hashes = static = fail; increase to 1.08.

---

## Axis 4 — Audio (TTS voice + music routing)

Cleared stack per D031: **OpenAI `tts-1-hd`**. ElevenLabs deferred to v0.2 per D022.

### Voice selection matrix (audio-producer owns)

| Register / use case | Voice | Speed | Why |
|---|---|---|---|
| Children's book narration, warm fable tone | `fable` | 0.92 | Default v0.1 voice — warm, unhurried. Matches the pilot project register. |
| Premium sports/commercial, confident male | `onyx` | 0.95 | Deep, authoritative. Default for motorsport / athletic / premium brand spots. |
| Calm documentary / explainer, neutral male | `echo` | 1.00 | Measured, informational. |
| Warm female lead, approachable | `nova` | 0.95 | Friendly, accessible. |
| Older authoritative narrator | `onyx` with `speed=0.88` | — | Slow delivery adds gravitas. |
| Energetic youth-market | `shimmer` | 1.05 | Brighter, faster-paced. |
| Child-voice character | `alloy` with `speed=1.02` | — | Closest to age-appropriate neutral-light register. |

### Routing rules (D040)

- **Operator-supplied audio contains narration** → direct-mux that file as the master. NEVER synthesize TTS on top. Check via Whisper transcript for non-music segments with >2 words of speech.
- **Operator-supplied music-only track** → use as bed; generate TTS narration on top via D034 concat-filter pattern.
- **No operator audio** → generate both music bed (skip for v0.1 — no cleared music generator) and TTS; for v0.1 that means silent or narration-only.

### Audio-track construction (D034)

Concat filter only. Never `amix`, never `apad`, never single-pass `loudnorm` on mixed tracks.

```
[0:a]aformat=sample_rates=44100:channel_layouts=stereo[a0];
[1:a]aformat=sample_rates=44100:channel_layouts=stereo[a1];
...[a0][a1]...[aN]concat=n=N:v=0:a=1[aout]
```

Each segment is either silence (`anullsrc` with `-t duration`) or VO. `loudnorm` IS permitted on standalone music tracks (audio-producer's music-only sub-protocol) — the D034 restriction applies specifically to VO+music mixing.

---

## Axis 5 — Reasoning depth (when premium reasoning pays off)

Routing-matrix roles are resolved to concrete models per active matrix. For the `anthropic` matrix (typical default):

| Role | Typical resolved model | When this matters |
|---|---|---|
| `creative` | claude-opus-4-x (premium) | Creative brief → shot list. The single most expensive creative call — worth the premium. One call, 90-180s thinking, sets the whole production. |
| `reasoning` | claude-opus-4-x (premium, high-reasoning) | Architecture, complex multi-step analysis. In this bundle, creative-director's fallback. |
| `critique` | claude-sonnet (standard, extra-high reasoning) | QA review — finding problems, not generating solutions. |
| `vision` | claude-sonnet with vision (or gemini-flash) | Intake-analyst frame analysis, qa-reviewer visual checks. |
| `fast` | claude-haiku / gpt-5-mini / gemini-flash | Mechanical routing decisions (which provider, which tier, which voice). |
| `coding` | claude-sonnet or gpt-5.x-codex | ffmpeg filter chains in post-producer. |
| `general` | claude-sonnet | Versatile fallback everyone terminates in. |

Rule of thumb: **the deeper the creative judgment call, the more you pay for the model**. Every other agent in the bundle works off the director's plan — they don't need premium reasoning to execute.

---

## Axis 6 — Vision analysis (intake + QA)

Intake-analyst and qa-reviewer both read images. Different providers have different strengths:

| Task | Model | Why |
|---|---|---|
| Extract literal printed text from page scans (D035) | gpt-4.1-mini or claude-sonnet | Both handle OCR-like tasks cleanly; gpt-4.1-mini is cheaper at volume (book page batches). |
| Identify a font from text crops (D037 — multi-sample, handwriting-vs-serif prompting) | claude-sonnet | Better at typography reasoning and distinguishing similar faces. |
| Analyze mockup-video frames (composition + notable elements) | claude-sonnet or gpt-4.1 | Either works; prefer whichever is cheapest in the current matrix. |
| Compare generated frame vs source ref (character-drift detection) | claude-sonnet | Best at identifying subtle identity-drift issues. |
| Read PDF/PPTX storyboard slides (scene + text verbatim + characters) | gpt-4.1-mini at volume | Deck analysis is bulk-throughput work. |

Batch vision calls in parallel where possible (intake-analyst does this via `ThreadPoolExecutor`). Vision is I/O-bound; serial calls waste wall time.

---

## Axis 7 — Delegate-time override

When a parent agent delegates to a child, the parent can override the child's default `model_role` via the `delegate(..., model_role="X")` parameter. Use this when:

- A shot needs hero-quality prompt engineering → delegate to `prompt-engineer` with `model_role="reasoning"` instead of its default
- A bulk batch of simple shots → delegate with `model_role="fast"` to reduce per-shot cost
- Vision-heavy analysis of operator material → delegate to any agent with `model_role="vision"`

Overrides are per-call; don't persist. Return to the agent's declared chain on the next invocation.

---

## Axis 8 — Cost awareness

Rough per-deliverable costs at current matrix rates (reference, not binding):

| Work item | Approximate cost |
|---|---|
| Creative-director full run (brief → shot list + style bible + character sheet) | $0.50 – $2.00 |
| Nano Banana Pro single 2K shot (ref-conditioned) | $0.05 – $0.15 |
| OpenAI gpt-image-2 single 1024×1536 shot (high quality) | $0.05 – $0.12 |
| Veo 3.1 lite 6s clip | ~$0.40 |
| Veo 3.1 fast 8s clip | ~$0.80 |
| Veo 3.1 standard 8s clip | ~$1.60 |
| OpenAI tts-1-hd per minute of output | ~$0.015 |
| Whisper transcription per minute of audio | ~$0.006 |
| Intake-analyst full pass on operator assets (~6 min) | ~$0.18 |
| QA-reviewer full manifest + visual checks | $0.20 – $0.60 |

### Budget guardrails (creative-director applies at shot-list authoring time)

- **Total Veo budget** = sum of per-shot tier costs. If a 32-shot trailer budgets 20× standard = $32 just for motion, that's acceptable for a deliverable; if it balloons to 50× standard = $80, push back to the brief and reallocate.
- **Ken-Burns budget** ≤ 20% of shots (per D032). Exceeding this means the project is quota-blocked, not just under-budgeted.
- **Regen budget** — 1 regen per character-critical shot, 0 for final-deliverable. Beyond that, escalate to operator for taste-call (D013).

---

## Axis 9 — Operator override discipline

The operator can pin any choice. Agents must respect operator pins even when the agent's heuristic would choose otherwise:

- `provider=gpt-image-2` in a shot spec → use gpt-image-2 even if the shot looks like Nano Banana territory
- `tier=standard` on an ambient shot → don't downgrade
- `voice=fable` even on a commercial brief → use fable

Document the pin in the shot spec's `notes:` field with the operator's reasoning. QA-reviewer will honor pins in its manifest.

Pins are the operator's taste call per D013. Agents are authoritative on hard rules (D033 validity, D036 amplitude thresholds, D030 ref downsize) but never on aesthetic preference.

---

## Quick reference card

Stick this on the wall:

```
 ┌──────────────────────────────────────────────────────┐
 │  BRIEF arrives                                       │
 │    → creative-director (creative, claude-opus)       │
 │                                                      │
 │  PHOTOREAL shot?  → Nano Banana Pro                  │
 │  TEXT in shot?    → OpenAI gpt-image-2               │
 │                                                      │
 │  Ambient shot?    → Veo lite (4-6s)                  │
 │  Normal motion?   → Veo fast (8s)                    │
 │  Hero beat?       → Veo standard (8s)                │
 │                                                      │
 │  Operator audio narrated?  → direct-mux (D040)       │
 │  Commercial register?      → onyx 0.95x              │
 │  Children's warmth?        → fable 0.92x             │
 │                                                      │
 │  Everyone terminates at "general" fallback           │
 │  Creative judgment calls cost premium — worth it     │
 │  Everything else runs on fast — also worth it        │
 └──────────────────────────────────────────────────────┘
```
