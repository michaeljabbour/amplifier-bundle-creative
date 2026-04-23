# Shot Spec Schema

Every shot in a `SHOT_LIST.md` conforms to this schema. Fields marked **required** must be present before handoff to `image-generator`. Fields marked *nullable* may be absent or null.

## YAML fields per shot

```yaml
shots:
  - id: S01                           # required — zero-padded 2-digit index
    duration: 6                       # required — seconds, must match tier (D033)
    tier: lite                        # required — one of: lite (4-6s), fast (8s), standard (8s)
    tags: [ambient-transitional]      # required — one of: character-critical, ambient-transitional,
                                      #                   final-deliverable, hero-beat
    composition: "..."                # required — what's on screen (characters, setting, action)
    camera: "..."                     # required — static, slow push-in, pan-left, handheld, etc.
    mood: "..."                       # required — one-phrase emotional register
    reference_pages: [page_04.png,    # required for existing-IP; null for greenfield
                      page_05.png]    #   per D028, ranked by setting-match (D029)
    page_text_overlay: "..."          # nullable — verbatim page text if shot ends on or carries a page
    vo_line: "..."                    # nullable — narration line if TTS narration in play
    motion_source: veo                # required — one of: veo, ken-burns, held-frame-from-prior
    audio_note: "..."                 # nullable — music cue, SFX intent, silence intent
    characters: [Boy, Grandfather]    # required — from CHARACTER_SHEET.md
    setting: interior-desk            # required — from STYLE_BIBLE.md's setting vocabulary
    action: "..."                     # required — what happens across the shot's duration
    handoff_from: S00                 # nullable — prior shot continuity
    handoff_to: S02                   # nullable — next shot continuity
```

## Validation rules

- `tier: lite` ⇒ `duration` ∈ {4, 5, 6}
- `tier: fast` ⇒ `duration == 8`
- `tier: standard` ⇒ `duration == 8`
- `tags: character-critical` ⇒ cannot use `motion_source: ken-burns` as default (D032)
- `reference_pages` ranked highest-to-lowest by setting-match (D029)
- If any shot references a character, `CHARACTER_SHEET.md` must have ref-page rankings for that character
- If any shot has a `page_text_overlay`, `book_text_extracted.json` must have that page's verbatim text

## Setting vocabulary

Valid values for `setting`: `interior-desk`, `interior-library`, `interior-hallway`, `pastoral-meadow`, `tree-grove`, `tech-monitors`, `night-network`, `abstract-gradient`, `title-card`, `empty-landscape`, `other` (must be declared in STYLE_BIBLE.md if used).

## Tags vocabulary

- **character-critical** — named character on-screen, identity must be protected. No KB fallback without approval.
- **ambient-transitional** — establishing shot, cutaway, coda. KB fallback acceptable on quota exhaustion.
- **hero-beat** — the punchline of a scene; the shot the campaign hangs on. Regenerate over fallback.
- **final-deliverable** — title card, credits, end card. KB with subtle zoom is always the right call.
