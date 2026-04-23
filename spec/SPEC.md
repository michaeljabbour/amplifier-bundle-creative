# Amplifier Creative Agent

**Status:** Draft v0.1 (frozen)
**Last updated:** 2026-04-21
**Owner:** internal team
**Scope:** Specification for a creative production agent system operating inside Amplifier, covering image and video generation routed across xAI, OpenAI, Google, Black Forest Labs, Recraft, and Ideogram APIs.

> **Status note (frozen).** This document is frozen at v0.1 as the design checkpoint. Subsequent resolutions, refinements, and course corrections are tracked in `DECISIONS.md` alongside this file — which supersedes anything here that conflicts. Only cut a new spec version when the conceptual frame itself changes; typo fixes and clarifications live in DECISIONS.

This document follows the project-context file conventions: PROJECT_CONTEXT, GLOSSARY, STRUCTURE, WAYSOFWORKING, PROVENANCE, EXPERIMENT_JOURNAL, CLAIMS_TRACKER, HANDOFF. Each section maps to a corresponding runtime file the agents read and write during a session.

---

## 1. PROJECT_CONTEXT

### 1.1 Purpose

Creative production is routing with memory. The model that fits shot three rarely fits shot seven. The character on page fourteen must match the cover. The pipeline has to remember decisions, justify them, and reproduce them later.

The Creative Agent system turns a creative brief into a set of approved visual and motion assets by orchestrating specialized sub-agents against a shared coordination substrate. No single model covers every need. The value lives in routing, continuity enforcement, and audit, not in any one provider.

### 1.2 In scope

Trailer production, storyboard generation, character-locked illustration sets, marketing assets, and short-form video for existing book and research projects. the pilot-project picture book and a conference deck are the first production targets.

### 1.3 Out of scope (v0.1)

Music and score composition. Interactive storyboarding UI beyond the Amplifier chat surface. Rights management beyond SynthID and C2PA provenance. Full 3D asset pipelines. Any pipeline feature that depends on Sora 2 past its 2026-09-24 deprecation.

### 1.4 Success criteria

A brief submitted to the system produces a reviewable deliverable with a complete provenance trail. Character consistency holds above the Critic threshold across shots. Total spend stays within the budget declared in the brief. An operator can resume or reproduce any session from the coordination files alone.

### 1.5 Non-goals

Replacing human creative direction. Every likeness decision, every publishing action, and every final deliverable requires explicit operator approval. The agent system accelerates production. It does not own taste.

---

## 2. GLOSSARY

**Surface.** A capability contract exposing a class of providers under a stable interface. Creative Agent adds three new Surfaces to the Amplifier primitive set: ImageGeneration, VideoGeneration, CreativeCritique. *(See DECISIONS D001 — the term "Surface" is superseded by "Tool protocol" in the next revision; the concept maps to Amplifier's existing Tool/Provider primitives.)*

**Character-critical.** A tag applied to any shot, frame, or asset that involves a named character, a child likeness, or a trademarked visual element. Triggers mandatory reference-image enforcement and operator approval at the Style Bible stage.

**Physics-required.** A tag applied to shots with fluid dynamics, falling objects, wind-blown cloth, water, smoke, or collisions where realism matters. Enables Sora 2 Pro routing. Without this tag, Sora routing is blocked.

**Drift vector.** A Critic output capturing how far a new generation has moved from the Style Bible reference on hue, character morphology, palette, and compositional language. Scored 0 to 1 where 1 is perfect match.

**Tier escalation.** Moving a generation job from Veo 3.1 Lite to Fast to Standard, or from Images 2.0 to Images 2.0 Thinking, based on Critic rejection. Every escalation is logged with reason.

**Last-frame handoff.** Passing the final frame of shot N as the first_frame input to shot N+1 in Veo 3.1. Required when shots are meant to connect without a visible cut.

**Style Bible.** The single source of truth for character appearance, palette, typography, mood, and forbidden elements. Every Visual or Motion Director call reads it before generating.

---

## 3. STRUCTURE

### 3.1 Agent roster

Seven agents. Narrow responsibilities. Thin conductor above them.

**Brief Interpreter.** Reads operator intent. Produces a structured creative spec. No generation tools. LLM only.

**Style Bible Keeper.** Maintains character sheets, palette, reference imagery, tone rules, forbidden elements. Owns the Style Bible. Uses image-gen tools only to produce reference assets the operator approves.

**Shot Planner.** Decomposes the brief into an ordered shot list. Tags each shot with `character-critical`, `physics-required`, `dialogue`, `final-deliverable`, or combinations. LLM only.

**Visual Director.** Generates still frames, character reference sheets, typographic assets, and vector outputs. Routes across Nano Banana Pro, Images 2.0 Thinking, Ideogram V3, Recraft V4, and Flux 2 Pro.

**Motion Director.** Generates video clips from approved stills. Routes across Veo 3.1 Standard, Fast, Lite, Sora 2 Pro, and Grok Imagine Video.

**Critic.** Scores every output against the spec and Style Bible. Flags drift. Uses Claude Opus 4.7 as primary vision judge, with GPT-5.4 and Gemini 3.1 Pro available for triangulation on high-stakes shots.

**Finisher.** Stitches approved clips, handles audio mix, produces the final encode. Wraps ffmpeg and audio models.

### 3.2 Coordination files

Three tiers matching the existing Amplifier tiered-context pattern.

**Tier 1: Session-persistent, always in context.**

- `PROJECT_CONTEXT.md`: brief, stakeholders, deliverable format, deadlines, budget
- `STYLE_BIBLE.md`: character sheets, palette hex values, mood references, forbidden elements, tone rules

**Tier 2: Stage-relevant, loaded per agent activation.**

- `SHOT_LIST.md`: the storyboard as a typed, tagged list
- `CONTINUITY_STATE.md`: last generated frames per character and setting, current drift scores
- `COST_LEDGER.md`: running spend by provider and tier, remaining budget, forecast

**Tier 3: Append-only audit trail. Written often, read rarely.**

- `ROUTING_LEDGER.md`: every provider and tier choice with reason
- `PROVENANCE.md`: every output with source prompt, refs, model version, SynthID, C2PA
- `CRITIC_JOURNAL.md`: every score with rationale
- `EXPERIMENT_JOURNAL.md`: anything that deviates from the default flow and why
- `CLAIMS_TRACKER.md`: explicit claims about what the output is and is not
- `HANDOFF.md`: human-approval checkpoints and their resolutions

### 3.3 Surface primitives

Three new capability contracts, composable with the existing Amplifier primitive set.

**ImageGeneration.**

```
inputs:   prompt, refs[], style_token, size, aspect, seed?
outputs:  image_url, provenance_record
caps:     text_to_image | image_to_image | text_in_image | vector
providers:
  - nano_banana_pro     (character consistency, conversational edit)
  - nano_banana_2       (fast default, 512px to 4K)
  - images_2_thinking   (multi-frame narrative, character continuity)
  - images_2            (default OpenAI image, 2K, best text-in-image)
  - ideogram_v3         (typography-first work)
  - recraft_v4          (logos, SVG vectors)
  - flux_2_pro          (camera-accurate photoreal)
  - flux_kontext        (character consistency specialist)
```

**VideoGeneration.**

```
inputs:   prompt, first_frame, last_frame?, refs[], duration, aspect, audio?
outputs:  video_url, provenance_record, last_frame_url
caps:     text_to_video | image_to_video | video_extension | video_edit
providers:
  - veo_3_1_standard    (4K, best lip-sync, $0.40/sec)
  - veo_3_1_fast        (1080p, $0.15/sec post-Apr-7 cut)
  - veo_3_1_lite        (720p, $0.05/sec)
  - sora_2_pro          (physics specialist, deprecating 2026-09-24)
  - grok_imagine_video  (10s 720p, unified SDK, anime/cyberpunk strong)
```

**CreativeCritique.**

```
inputs:   output_url, spec, style_bible, tags[]
outputs:  score (0-1), accept|reject, drift_vector, suggested_fixes[]
caps:     character_consistency | style_adherence | prompt_adherence
providers:
  - claude_opus_4_7_vision   (primary judge)
  - gpt_5_4_vision           (triangulation)
  - gemini_3_1_pro_vision    (triangulation)
```

Keeping Critique as a separate Surface with its own provider pool means the system can triangulate on high-stakes shots. Require two-of-three approval when a shot is tagged `final-deliverable` and `character-critical`.

---

## 4. WAYSOFWORKING

### 4.1 Routing behaviors

Visual Director escalates tiers only when the Critic rejects twice at the current tier. Every escalation writes to `ROUTING_LEDGER.md` with the Critic's rejection reason and the new tier selected. Silent escalation is not permitted.

Motion Director routes to Sora 2 Pro only when the Shot Planner has applied the `physics-required` tag. The tag originates in the Brief Interpreter based on prompt features: water, fluids, falling, wind-blown cloth, collisions, or explicit operator instruction. Sora routing is otherwise blocked, including on operator override. To route to Sora, the operator re-tags the shot. The system declines to infer intent.

Character-critical shots require the three-reference-image path in Veo 3.1. When the Style Bible has fewer than three approved references for a character, the job halts and the Style Bible Keeper requests additional references from the operator via `HANDOFF.md`.

Images 2.0 Thinking is the default for any shot tagged `character-critical` plus `storyboard` or `multi-scene`. Base Images 2.0 and Nano Banana 2 take single-scene, single-character work without continuity demand.

### 4.2 Continuity behaviors

Before any generation, the active Director reads the latest `CONTINUITY_STATE.md`. When the state shows drift above threshold (Critic score below 0.80 versus the Style Bible reference), regeneration is forced with tighter reference weighting. The drift threshold sits at 0.80 for general work, 0.90 for character-critical work, and 0.95 for likeness involving children.

Motion Director passes the final frame of shot N as `first_frame` for shot N+1 unless the Shot Planner has marked a deliberate cut between those shots. Cuts are explicit, not a fallback.

Style Bible updates ripple. When an operator edits a character reference, the Style Bible Keeper marks all prior generations that depended on the old reference as `needs_review` in `CONTINUITY_STATE.md`. The Critic re-runs against new references on the next session open.

### 4.3 Budget behaviors

Every agent reads `COST_LEDGER.md` before acting. If remaining budget falls below 1.5x the forecast cost of the next action, the agent halts and writes to `HANDOFF.md` asking for operator approval with a cost breakdown.

The Critic runs on every non-trivial output by default. Auto-approval fires only when three conditions all hold: tier is Lite, Critic score exceeds 0.92, and no character-critical tag applies. This keeps cheap iterations cheap and expensive iterations thoroughly reviewed.

Forecast is recomputed after each Critic pass. The cost forecast accounts for expected regeneration rate by shot type, informed by the rolling CRITIC_JOURNAL history.

### 4.4 Human-in-loop behaviors

Any operation touching a character likeness requires operator approval at the Style Bible stage. For the pilot project project this applies to every named character and every child figure. The gate is structural, not procedural. The Style Bible Keeper cannot register a new character reference without a `HANDOFF.md` entry confirmed by the operator.

Final deliverable operations (4K export, publish, share, upload to IngramSpark, post to LinkedIn, commit to a repo) always require explicit operator confirmation. No agent in the system holds publishing authority.

Cost ceilings are set at session start in `PROJECT_CONTEXT.md`. Crossing a ceiling halts the session. The agents do not request ceiling increases on their own; the operator adjusts the budget explicitly.

### 4.5 Rolling ROI control

Every agent emits a per-action cost, latency, and Critic-score triple. The Finisher aggregates these into a session summary at completion time, appended to `EXPERIMENT_JOURNAL.md`. Patterns across sessions feed the the team's internal research program.

---

## 5. Example session flow

Use case: 60-second pilot project book trailer for the a conference presentation.

> **Note.** This section depicts a sync-looking flow for readability. The real async semantics — `video-mcp` returns a job_id immediately, lifecycle events stream via Amplifier Hooks — are documented in DECISIONS D003 and D011. Treat the steps below as logical order, not literal blocking calls.

1. Operator submits brief: "60-second trailer for the pilot project, watercolor aesthetic matching the illustrator's illustrations, warm afternoon light, ending on the cover reveal."
2. Brief Interpreter writes `PROJECT_CONTEXT.md` with budget ($30 cap), deliverable (4K master, 1080p web cut), deadline (72 hours).
3. Style Bible Keeper loads existing the illustrator reference assets, extracts palette, writes `STYLE_BIBLE.md` with character sheets and forbidden elements (no photorealistic faces, watercolor only). Requests operator approval on character likenesses via `HANDOFF.md`.
4. Operator approves in Amplifier UI.
5. Shot Planner decomposes the trailer into 8 shots. Tags shots 1, 3, 5, 7, 8 as `character-critical`. Tags shot 4 (puddle splash) as `physics-required`. Tags shot 8 as `final-deliverable` (the cover reveal).
6. Visual Director generates the opening still with Nano Banana Pro and three reference images from the Style Bible. Critic scores 0.94. Approved. `CONTINUITY_STATE.md` updated with the still as anchor.
7. Motion Director generates shot 1 with Veo 3.1 Standard, passing the approved still as `first_frame`. Critic scores 0.89. Approved.
8. Shots 2, 3 proceed on Veo 3.1 Fast with last-frame handoff.
9. Shot 4 routes to Sora 2 Pro (physics-required tag). Critic scores 0.87. Approved. Last-frame extracted for handoff to shot 5.
10. Shots 5, 6, 7 proceed on Veo 3.1 Standard with character references.
11. Shot 8 (cover reveal, final-deliverable + character-critical) triggers triangulated Critic. Opus 4.7, GPT-5.4, and Gemini 3.1 Pro all score above 0.90. Approved.
12. Finisher stitches all shots, layers in the approved audio track, produces a 4K master and a 1080p web cut.
13. Finisher writes session summary to `EXPERIMENT_JOURNAL.md`: total spend $23.40, peak Critic score 0.96, weakest Critic score 0.87, total generation time 42 minutes, escalation count 2.
14. `HANDOFF.md` requests operator approval for export. Operator confirms. Files land in the project deliverables folder.

A week later, asked why shot 4 used Sora 2 Pro instead of Veo 3.1 Standard, the answer sits in `ROUTING_LEDGER.md` with the Critic's physics-quality score on a Veo pilot attempt and the operator's physics-required tag confirmation.

---

## 6. PROVENANCE

Every generated asset carries a provenance record. Fields:

- `generation_id`: UUID
- `session_id`: UUID
- `agent`: Visual Director, Motion Director, or Finisher
- `provider`: specific model string (e.g. `veo-3.1-generate-preview`)
- `tier`: lite, fast, standard, pro, thinking
- `prompt`: exact prompt string sent to provider
- `refs[]`: reference image URLs with their own provenance IDs
- `style_token`: pointer to the STYLE_BIBLE version active at generation time
- `synthid`: watermark record where available (Veo, Imagen, Nano Banana)
- `c2pa`: Content Credentials record where available
- `critic_scores[]`: array of critique results with judge model
- `cost`: per-generation spend
- `latency`: seconds to completion
- `approved_by`: operator ID on human-gated approvals

Provenance records append-only. Deletion is a CLAIMS_TRACKER event, not a PROVENANCE edit.

---

## 7. EXPERIMENT_JOURNAL

Any deviation from the default routing, tiering, or gating policy writes an entry. Template:

```
## YYYY-MM-DD HH:MM session=<id>

What changed: <specific deviation>
Why: <operator reason, critic reason, or system reason>
Outcome: <what shipped, what was rejected, what the score was>
Signal for the policy: <do we update the default next time>
```

The goal is not to accumulate anecdotes. The goal is to generate evidence the the team can fold back into routing heuristics and tier thresholds.

---

## 8. CLAIMS_TRACKER

Every deliverable ships with claims about what it is. For pilot-project and other client work these matter for IP, disclosure, and trust. Template:

```
## Claim: <the thing being asserted about the asset>

Scope: <what assets this claim applies to>
Evidence: <provenance_ids, critic_scores, operator_approvals>
Expiration: <when this claim needs re-verification>
Related claims: <cross-references>
```

Example claims:
- "Character likenesses derive from approved the illustrator reference assets, not photorealistic generation."
- "All video outputs carry SynthID watermarks as a condition of delivery."
- "No child likeness in the pilot-project trailer was generated without reference to pre-existing approved illustrations."

---

## 9. HANDOFF

Human approval checkpoints. Fixed format to keep turnaround fast.

```
## HANDOFF <id> | <priority> | <session>

Request: <what approval is needed>
Context: <minimum operator needs to decide>
Cost if approved: <dollars>
Cost if declined: <sunk + rework estimate>
Default if no response in <N hours>: <halt | proceed with fallback>
```

Priorities: P0 (character likeness, publish), P1 (tier escalation, budget ceiling), P2 (routing deviation, style exception). P0 blocks the session. P1 blocks the current task. P2 logs and continues with the safer default.

---

## 10. Roadmap

**v0.1 (this spec).** Three Surfaces, seven agents, nine coordination files. Ships against the existing Amplifier primitive set.

**v0.2.** Music and score composition via a new AudioGeneration Surface (Lyria 3, ElevenLabs Music, MAI-Voice-1). Triggered by Finisher when the brief calls for original score.

**v0.3.** Interactive storyboard UI surfaced in the Amplifier chat pane. Shot list becomes editable inline, drag-reorder, per-shot re-generation.

**v0.4.** Rights and licensing Surface covering Adobe Firefly indemnified paths for commercial deliverables where legal exposure matters.

**Known cliffs.** Sora 2 API deprecation on 2026-09-24. Either front-load Sora-dependent work, wait for the successor, or accept Veo physics for all future sessions. Decision owner: internal team. Decision deadline: 2026-08-15. *(See DECISIONS D010 — resolution is "stub only, skip implementation" for v0.1.)*

---

## 11. Open questions

1. Critic triangulation threshold. Two-of-three on final-deliverable character-critical is the current rule. Should it be three-of-three for any child likeness in pilot project?
2. Cost ceiling behavior on deadline-critical sessions. Current default halts the session. Should there be a deadline-override path that raises the ceiling with secondary operator confirmation?
3. Style Bible versioning. Append-only or mutable with git-style history? Argument for append-only: provenance clarity. Argument for mutable: iteration speed during early sessions. *(See DECISIONS D014 — resolved as append-only.)*
4. Provider availability fallback. When Veo 3.1 Standard returns a transient error, the current design retries once then escalates to Sora 2 Pro if the shot allows. Should the fallback be Grok Imagine Video instead to stay unified with xAI SDK patterns?
5. MAI integration. MAI-Voice-1 for narration is obvious. Is there a v0.2 path to route some generation through MAI-Image-2 for internal Microsoft deliverables where first-party infrastructure matters?

---

## Appendix A: Starter templates

### A.1 STYLE_BIBLE.md template

```markdown
# Style Bible: <project>

## Characters

### <Name>
- **Visual anchor refs:** <3+ image URLs with provenance IDs>
- **Morphology notes:** <shape language, proportions, signature details>
- **Palette:** <hex codes, named swatches>
- **Forbidden:** <what the character never does or wears>

## Palette

- Primary: <hex>
- Secondary: <hex>
- Accent: <hex>
- Forbidden colors: <hex>

## Mood references

- <image url> | <what it anchors>

## Tone rules

- <bullet per rule>

## Forbidden elements

- <list>
```

### A.2 SHOT_LIST.md template

```markdown
# Shot List: <project>

## Shot 1
- **Duration:** 6s
- **Aspect:** 16:9
- **Tags:** character-critical, dialogue
- **Characters:** <name(s)>
- **Setting:** <one line>
- **Action:** <one line>
- **Audio:** <line if dialogue, otherwise ambient description>
- **Handoff from shot:** N/A (opening)
- **Handoff to shot:** 2

## Shot 2
...
```

### A.3 ROUTING_LEDGER.md entry template

```markdown
## YYYY-MM-DD HH:MM session=<id> shot=<n>

Decision: <provider> at <tier>
Reason: <why this and not the default>
Critic score before: <n/a or number>
Critic score after: <number>
Cost: <dollars>
```

### A.4 HANDOFF.md entry template

```markdown
## HANDOFF <id> | P<0|1|2> | session=<id>

Request: <what approval is needed, one sentence>
Context: <two or three sentences max>
Cost if approved: $<n>
Cost if declined: $<n> sunk, $<n> rework estimate
Default if no response in <n> hours: <halt | proceed with fallback>

---
Resolution: <approved | declined | modified>
Resolved by: <operator>
Timestamp: <iso>
Notes: <optional>
```

---

## Appendix B: Minimal provider adapter interface

Every provider in every Surface implements the same adapter contract. Adding a new provider (MAI-Image-3, Sora 3, Qwen Image) becomes a one-file addition.

```python
class ProviderAdapter:
    name: str
    surface: Literal["image", "video", "critique"]
    capabilities: set[str]
    cost_per_unit: Callable[[Request], float]
    estimate_latency: Callable[[Request], float]

    async def generate(self, req: Request) -> Response: ...
    async def health_check(self) -> bool: ...
    def to_provenance_record(self, resp: Response) -> dict: ...
```

The conductor routes on `capabilities` and `surface`. Cost and latency feed the COST_LEDGER forecast. Provenance record shape is provider-specific but conforms to the PROVENANCE schema in Section 6.

*(See DECISIONS D015 — this adapter interface is rewritten to conform to Amplifier's existing Provider module protocol. foundation-expert validation gates the implementation.)*

---

*End of spec v0.1. Iterate in `DECISIONS.md`. Major changes cut a new version.*
