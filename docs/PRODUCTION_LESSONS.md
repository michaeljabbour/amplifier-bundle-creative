# Production Lessons — Pilot-Project MVP Cycle

**Status:** Living document — captures what we learn as we ship real projects, so future uses of the Creative bundle have the benefit of this experience.

**First cycle:** 2026-04-21/22. the pilot-project picture book → ~5:15 narrative animation. Two deliverable masters (clean + titled), aligned to a user-supplied 5:15 music track. 32 shots. Reference-image-first generation throughout.

---

## What the AI Producer Must Understand

A children's picture book animation is **not** 32 shots stitched with voice-over. It is:

1. **A piece of music** with a shape (in our case, 5:15 given as a hard constraint by the operator) — the music *drives the edit*. Duration is not something the visuals decide and the music follows. The music is fixed and the visuals fit its shape.
2. **Literal page text** flowing across the animation — every page that has printed narrative prose should surface that prose on screen as the corresponding visual plays. Not paraphrases invented by the producer. Not anchor-moment VO lines only. The **book's own words** in the **book's own voice**, and ideally in the **book's own typography**.
3. **Narration** that reads the book like someone reading aloud to a child — warm, unhurried, adult-but-gentle. TTS voice choice matters more than most picture-book pipelines assume.
4. **Visual continuity with the source art** — reference-image conditioning (D028) is non-negotiable for existing-IP reproduction. Setting-match refs (D029) matter more than face-clarity refs.
5. **Consistent mastering** — all deliverables are the same duration, same aspect, same codec, same audio pipeline. The only difference between "clean" and "titled" is the text-overlay layer. If the two masters are mastered differently, the user is right to call it a failure.

The producer's first move on any new project is **understand the piece**. Read the book (vision-extract the literal text per page). Listen to the music (probe duration and loudness profile). Match the visuals and text to the music's shape. Only then start generating.

---

## What Went Right (Keep These Patterns)

### 1. Reference-image-first generation (D028/D029)
Passing actual source pages to Nano Banana Pro produced character-faithful frames. The failure mode — text-only prompts with adjectives and hex codes — reliably produced "generic watercolor boy" outputs that didn't read as the user's character. D029 refinement (setting-match refs over face-clarity-ranked refs) was validated by direct operator comparison of v2 vs v3 first-frame tests.

### 2. Fallback ladder for provider failures (D010, D032)
When Gemini quota exhausted mid-run after ~27 Veo jobs, Ken-Burns fallback on already-generated Nano Banana frames preserved character fidelity and narrative continuity with zero additional API calls. The fallback operates on the correct frame; viewers don't notice the motion-reduction on short ambient beats (Shots 20, 24, 28 in pilot project).

### 3. Runtime file-storage discipline (D025)
Writing only to the user's `~/Downloads/{project}-{timestamp}/` directory proved itself: the user can navigate, inspect, move, and delete artifacts without hunting through application-controlled caches. This discipline also made the operator's late-stage workflow — dropping `operator_audio.mp3` into the run directory for the next iteration — work without any ceremony.

### 4. Book text extraction as first-class producer input
Vision-extracting the literal book text from each of the 16 source pages took ~30 seconds of API time and produced the verbatim script the animation needed. This should be a standard pre-production step for any existing-IP animation going forward.

---

## What Went Wrong (And What To Change)

### 1. VO mixing — three broken patterns before a working one

Three mixing approaches failed before the fourth worked:
- **v1**: `adelay + apad + amix(normalize=0, duration=longest)` — only the first VO line was audible. Root cause: `apad` made every stream infinite, `amix`'s default `dropout_transition=2s` attenuated later VOs.
- **v2**: `anullsrc silent base + adelay + amix(normalize=0)` — almost completely silent (5/10250 frames with signal). Silent base dominated the mix somehow.
- **v3**: concat demuxer + `loudnorm=I=-16:TP=-1:LRA=11` single-pass — near-silent. Single-pass loudnorm on short speech clips mis-estimates integrated loudness and attenuates toward target, producing silence.
- **v4 (WORKING)**: concat **filter** (not demuxer) with `aformat=sample_rates=44100:channel_layouts=stereo` on each segment, no loudnorm, no amix. Linear segmentation in time (silence[gap] + VO + silence[gap] + VO + ... ) concatenated via `concat=n=N:v=0:a=1`. Verified audible at every anchor.

**Lesson for the bundle:** ship a **tested VO-mixing helper** in a post-production toolkit so future projects don't rediscover these traps. Pattern: never use `amix` + `apad`; never use `loudnorm` single-pass on <5s clips; always use `concat` filter for sequence-based audio layering. Captured formally in D034.

### 2. QA theater — "audio stream present" is not "audio audible"

V1 of the masters passed `ffprobe` QA: audio stream present, correct codec, correct duration. But only the first VO line was actually audible. The QA checklist was wrong. Real audio QA must **sample amplitude at multiple timestamps** (specifically the anchor points where audio is expected to appear) and confirm non-zero signal. Codified in D036.

### 3. Font identification — "medium confidence Times New Roman" was wrong

First pass used OpenAI vision on a center-cropped page and got "Times New Roman family, medium confidence, alternatives: Georgia, Baskerville, Palatino." Deployed Baskerville. User rejected: "none of them have my font."

Second pass used vision on three separate high-resolution text crops from three different pages. Consensus: **handwritten style** (guesses: Architect's Daughter, Patrick Hand, KG Second Chances Sketch; macOS equivalents: ChalkboardSE, Bradley Hand Bold). Night and day from the first pass.

**Lesson:** font ID requires **multiple text samples across the source material** and **explicit prompting for handwriting vs. system-serif distinctions**. Captured in D037.

### 4. Text timing was narrator-paced, not book-page-paced

V1 overlaid text at 9 anchor moments (the VO anchor points). The user expected text **across the animations** — every page with printed text should surface its text on the corresponding shot. V2 overlays 30 text blocks across the 32 shots, each showing the literal text for that shot's anchor page.

**Lesson:** for existing-IP animations, the rule is "one text overlay per anchor page with text, timed to its shot," not "text at narration anchors." Captured in D035.

### 5. Music was an afterthought in v1

V1 had no background music at all — the user had to mention it in feedback, then drop their `operator_audio.mp3` into the run directory. V2 mixed the 5:15 music at constant -10dB with VO rides and reached 5:15 exactly by extending the visual timeline via held frames.

**Lesson:** **ask about music on project intake.** If the operator has a track, it's the skeleton the whole edit hangs on. If they don't, plan to source/generate one. Captured in D038.

### 6. Duration should be driven by music, not invented

V1 was 3:58 — a number I invented from "32 shots × 8s average." The music is 5:15, and the user's implicit expectation was a 5:15 animation. The visual timeline should extend or compress to fit the music, not the reverse. Held-frame extensions on contemplative coda beats are the reliable tool.

---

## Concrete Bundle Improvements (Derived From This Cycle)

### Post-production toolkit (new, phase 2b)

A set of tested helpers the bundle exposes as reusable building blocks:

- `produce_vo_track(clips: list[tuple[float, Path]], total_duration: float) -> Path` — concat-filter implementation with aformat normalization; no `amix`, no `apad`, no `loudnorm`.
- `mix_music_vo(music: Path, vo_track: Path, music_db: float = -10, vo_delay_s: float = 0) -> Path` — constant background music + VO rides, with explicit delay to absorb fade-in.
- `extend_via_held_frame(shot_mp4: Path, frame_png: Path, target_duration: float) -> Path` — append a frozen final frame to a short clip to reach a target duration.
- `render_text_overlay_pngs(specs: list[TextOverlaySpec], font: Path, canvas: tuple[int, int]) -> list[Path]` — Pillow-based PNG rendering of title cards with translucent plates, sized for overlay.
- `overlay_title_cards(video: Path, overlay_specs: list[TimedOverlay]) -> Path` — ffmpeg overlay filter chain with per-overlay `enable='between(t,X,Y)'` ranges.
- `verify_audio_audible_at(master: Path, timestamps: list[float]) -> QAReport` — decode-and-sample RMS check at specific timestamps. This is what QA should actually look like.

### Project-intake checklist (new, phase 2a.3)

Before any generation begins, the producer must answer:

1. **Is there existing IP we're reproducing?** If yes, extract literal text and identify font via multi-sample vision.
2. **Is there source audio/music?** If yes, probe duration — this drives the edit. If no, what's the target duration and what music do we source/generate?
3. **What is the story's narrative arc?** Verbatim, by page. This becomes the text overlay timing and the VO script.
4. **What are the character-canonical reference pages?** Per D028/D029, including setting-match concerns.
5. **What is the operator's QA standard?** Visual match, audio presence at every line, matching duration, consistent mastering across variants.

### Shot-list format updates (phase 2a.3)

Every shot in a `SHOT_LIST.md` (D033, extended here) must include:

- `page_text_overlay` field: the literal book text to show during this shot, or null for pages without text.
- `vo_line` field: exact narration text (should match or paraphrase the page_text_overlay) or null for silent shots.
- `motion_source`: `veo-3.1-<tier>` or `ken-burns-still` (per D032).

This locks the text-timing discipline into the shot spec so the producer doesn't have to improvise it at stitching time.

---

## Self-Reflection: The Role Shift

The operator's feedback after v1 — "take more of a producer role in understanding the original book and story, how you want to create the images and narration, layout of music, etc., and the product" — was the key frame change.

In v1, I was an executor: the user says "make a trailer," I cut a 60-second social trailer, then re-scoped to "5-minute animation," I produced 32 shots of what I thought were the right beats with narration I paraphrased, overlays I picked at anchor moments, a font I guessed, and no music.

In v2, I produced:
- **Book read** (vision-extracted literal text from all 16 pages) before deciding what narration or overlays to use
- **Music driven timing** (5:15 exactly, extended via held frames not re-generated shots)
- **Font verified** (multiple text samples, ChalkboardSE chosen because the book is hand-drawn not typeset)
- **Page-accurate overlays** (30 text blocks, one per anchor page with text)
- **Single consistent mastering pipeline** (both `_clean` and `_titled` share the same silent base + same audio mix; only the text layer differs)

The delta between v1 and v2 is what the word "produce" means. The operator was right to name it.

---

*Update this file every production cycle. Each new project should add a dated section capturing what was learned. the pilot-project cycle above is the first entry.*

---

## Second cycle: 2026-04-22 evening (v4 and v4.1)

**What triggered it:** The operator reported four distinct issues with v3:
1. "Shot 04 (kid at desk) and shot 14 (hand painting at easel) didn't land."
2. "Audio is not in sync."
3. "Narration isn't smoothly across the entire film."
4. "Run a tighter ship in terms of how the files are organized." (this one was addressed in v3→v4 via D039)

And later, during v4:
5. "Gaps in the videos between scenes sometimes."
6. "Deeper analysis of the wording on screen to match the audio."

The operator then disclosed three reference assets that had been sitting in their Downloads folder the whole time: `operator_audio.mp3` (315s — we knew about this), `operator_mockup.mov` (a 309s manual mockup video showing their preferred visual layout with narration-synced text overlays), and `operator_deck.pptx`/`.pdf` (a 15-slide PowerPoint storyboard).

The AI producer had not looked at any of the mockup material through v1-v3. It had been running on the book page scans + its own CHARACTER_SHEET only, while the operator had drawn everything.

### What the AI got wrong this cycle (and has now fixed)

#### 1. The double-narration bug

The operator's MP3 already contained a full human-narrator reading of the book, professionally timed to the music. The AI producer had been treating it as "music" and generating its own OpenAI TTS narration layered on top at AI-chosen timestamps. The v3 clean master contained *two narrations playing over each other* — the operator's human voice faintly (because music was attenuated to -10dB and the narration was part of that track) and the AI's synthetic fable voice loudly (at +3.5dB). Operator hearing: "not in sync" — because the two versions said similar lines at slightly different times.

**Fix** (D040): On any operator-supplied audio, transcribe with Whisper first. If non-music segments contain narration, that audio is the master track; direct-mux it, do not synthesize TTS on top. Whisper transcription costs pennies and runs in 30 seconds. Skipping it cost four production cycles.

#### 2. Asset-intake blindness

The operator's mockup video showed exactly which characters should be in each shot, where text should appear, and how narration aligned with visuals. The PPTX deck showed the complete 15-scene storyboard. The AI producer ignored both and invented compositions via generic prompts, missing:
- An entire 40-second opening question-card sequence the operator had designed ("[opening question card excerpt], can we rely on humans to do the right things?")
- The title card with author and illustrator credits
- That the Grandfather *stands behind* the seated Boy at the laptop (not beside him)
- That shot 14 features *three* creative tools (mic + easel + laptop), not just an easel and a paintbrush
- That shot 14's laptop screen shows the Light's smiling face — the whole point of that beat

All of this was visible at first glance in assets the operator had in hand the whole time.

**Fix** (D041 + D044): Multi-modal operator reference intake is mandatory before any generation. Run Whisper on audio tracks, extract video frames at 15s intervals and vision-analyze each, render PDF/PPTX slides to PNG and vision-analyze those too. Produce a synthesized `operator_intent_map.md` in `02_preproduction/`. Every downstream "should X look like Y?" question gets answered by cross-referencing this map, not by AI inference.

#### 3. Text overlays timed to shots, not narration

v4's text overlay timing was tied to shot cut points. A 17-second shot got one overlay for its full duration, regardless of whether the narration inside that shot was one sentence or four. Specific failure: shot 05 spanned 93-101s, narration "[Light's first line]" landed 90-92s, v4 showed the "HELLO" text from 93.5-100.5s — **after** the narrator finished saying it.

**Fix** (D042): Overlay `enable` ranges derive from Whisper segment timestamps, not from shot cuts. Each narration segment gets its own overlay. Silent music passages get no text on screen — deliberate breathing room, not sticky text. v4's 30 shot-anchored overlay blocks became v4.1's 35 narration-precise events.

#### 4. Static held-frame extensions feel like gaps

When a shot was extended beyond its Veo-generated motion duration via held-frame, the tail frame was completely frozen. Shot 03 had 11 seconds of frozen frame. Shots 12, 13, 27, 28, 29 each had 4-6 seconds of frozen frame. Operator: "gaps in the videos between scenes sometimes." No literal black frames — but when the camera stops moving mid-animation, the viewer reads it as a pause or glitch.

**Fix** (D043): Held-frame extensions must carry subtle Ken-Burns zoom (1.04× over hold duration). Static holds are prohibited. Bundle toolkit's `extend_via_held_frame` helper defaults to KB with an optional `static=False` flag; verification step checks frame-hash at two points within the hold and fails if identical.

### The role shift — this time more complete

In v3 we talked about the shift from "executor" to "producer" (reading the book, identifying the font properly, driving the edit from the music's shape). That was a good frame but incomplete — the producer still wasn't *listening to the audio they'd been given* or *reading the storyboard the operator had drawn*.

In v4 and v4.1, the producer added:
- **Transcribe before generating.** Treat operator audio as speech until proven music-only.
- **Read the storyboard.** If the operator made a mockup, that's the deliverable spec; generate toward it, not past it.
- **Serve the audio, not the visuals.** Shot durations, text timings, cut points — all derive from Whisper segment timestamps, not AI preferences.
- **Never freeze the camera.** Held extensions use Ken-Burns. The viewer shouldn't be able to tell where Veo ended and the hold began.

### Concrete bundle improvements derived from this cycle

Adds to the post-production toolkit (phase 2b):

- `whisper_transcribe(audio_path: Path, granularity: str = "segment") -> WhisperResult` — OpenAI Whisper wrapper with segment timestamps; checks for narration presence.
- `is_narrated(whisper_result) -> bool` — returns True if any non-music segment has meaningful speech; drives D040 routing.
- `extract_video_frames(video: Path, interval_s: float = 15) -> list[Path]` — samples video at intervals for intent-map analysis.
- `vision_analyze_frames(frames: list[Path], question: str) -> list[dict]` — parallel vision analysis via gpt-4.1-mini.
- `pdf_to_pngs(pdf: Path, dpi: int = 110) -> list[Path]` — via `pdftoppm` for storyboard decks.
- `build_operator_intent_map(assets: OperatorAssets) -> IntentMap` — composes the above into a single synthesized reference map.
- `extend_via_held_frame(shot: Path, frame: Path, target_duration: float, kb_zoom: float = 1.04) -> Path` — held extension with built-in Ken-Burns (D043); includes frame-hash verification step.
- `render_narration_synced_overlays(whisper_result, text_map) -> list[TimedOverlay]` — produces overlay specs with `enable` ranges tied to Whisper segment start/end (D042).

### A note on the four-cycle cost

v1 through v4.1 is four full production cycles of a 5:15 picture-book animation. Each cycle took roughly 15-60 minutes of producer time plus API costs. The operator reviewed between each.

Roughly half of those cycles could have been avoided by doing the asset intake *once*, on day one, before any generation. The operator had provided everything needed. The AI producer's job was to *look at what they provided* before building. It didn't.

This is now the top line of the project-intake checklist.
