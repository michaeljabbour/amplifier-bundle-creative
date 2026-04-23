# Operator Intent Map — {project-name}

**Author:** intake-analyst
**Version:** v1 (regenerated on each new intake run)
**Decisions:** D040, D041, D044

## Purpose

Single authoritative synthesis of everything the operator supplied. Every downstream agent reads this instead of re-interpreting raw assets. `creative-director` reads this first; every "should X look like Y" question is answered by cross-referencing this map.

## Asset inventory

| Asset | Present? | Path | Analysis artifact |
|---|---|---|---|
| Audio track | {yes/no} | `01_source/*.mp3` | `02_preproduction/operator_assets/audio_transcript.json` |
| Reference video | {yes/no} | `01_source/*.mov` | `02_preproduction/operator_assets/mockup_analysis.json` |
| Storyboard deck | {yes/no} | `01_source/*.pdf` | `02_preproduction/operator_assets/deck_analysis.json` |
| Source pages | {yes/no} | `01_source/book_pages/` | `02_preproduction/book_text_extracted.json` + `font_identification.json` |
| Brief / notes | {yes/no} | `01_source/*.md` | summarized inline below |

## Audio master decision (D040)

- **Is narrated:** {true / false}
- **Narration master:** {file path if narrated; null if music-only}
- **Routing:** {"direct-mux via audio-producer" if narrated, "TTS generation planned" if music-only}
- **Music duration:** {seconds} — drives target animation length per D038

## Narration timeline (from Whisper)

Only populated if `is_narrated: true`. Segment timestamps drive text-overlay timing (D042) and shot-cut alignment.

| Start (s) | End (s) | Text |
|---:|---:|---|
| 0.0 | 40.0 | (music only — no narration; opening visual carries) |
| 40.0 | 44.0 | "The {subject} by {author}." |
| ... | ... | ... |

## Visual-flow map (from mockup frames + deck slides)

Per operator reference:

| Operator time (s) | Source | Composition | Text visible | Notes |
|---:|---|---|---|---|
| 0 | mockup frame @ 0s / deck slide 01 | grass + dark sky, text overlay | "{opening question}" | 40s hold; title card follows |
| 45 | deck slide 02 | three characters seated on grass facing sky + title | "{title} / {credits}" | title card |
| 60 | deck slide 03 + mockup @ 60s | two children reading on meadow | "{page 01 text}" | matches page_04 |
| ... | ... | ... | ... | ... |

## Text-overlay content (from book_text_extracted.json + deck slides)

Verbatim text per intended timestamp. `post-producer` uses this directly — never paraphrases (D035).

| Narration start (s) | Verbatim text (for overlay) |
|---:|---|
| 51.0 | {first narration line} |
| 58.0 | {second narration line} |
| ... | ... |

## Character compositions

From mockup frames + deck slide annotations — specific staging choices the operator has made.

- **{character-1}:** {role + wardrobe + consistent staging note}
- **{character-2}:** ...

## Source material — what exists vs what must be generated

- **Exists (use directly via reference conditioning per D028):** {list of book pages / existing images / approved refs}
- **Must be generated:** {list of scenes/compositions with no source — greenfield portions}

## Font identification (from multi-sample vision per D037)

- **Primary guess:** {font family + weight}
- **Platform fallback:** {e.g., `ChalkboardSE.ttc` on macOS if the primary isn't installed}
- **Confidence:** {low / medium / high}
- **Features observed:** {e.g., "hand-drawn crayon texture, uppercase-only, slight ink bleed"}

## Brief summary

Condensed from `01_source/*.md`:

- **Deliverable type:** {commercial / trailer / hero-still campaign / animated short}
- **Target duration:** {s}
- **Tone:** {one phrase}
- **Audience:** {one phrase}
- **Key constraints:** {from brief}
- **Hard no's:** {things the brief forbids}

## Null-intake case (when no assets supplied)

- **Operator confirmed "no" on:** {audio / mockup / deck / source IP / brief}
- **Verbal brief captured:** {inline}
- **Target format:** {duration, aspect ratio, delivery}

## Completion

- [ ] All applicable intake steps from `creative:context/INTAKE_CHECKLIST.md` complete
- [ ] All analysis artifacts written to `02_preproduction/operator_assets/`
- [ ] Operator confirmed on any null-intake rows
- [ ] Ready for `creative-director` handoff
