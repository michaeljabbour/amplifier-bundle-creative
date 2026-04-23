# Shot List — {project-name}

**Producer:** creative-director
**Version:** v1
**Total duration:** {music_duration_s}s (driven by music per D038)
**Total shots:** {N}
**Audio:** {operator-provided | synthesized-TTS | silent}

## YAML shot list

```yaml
# One entry per shot; see context/SHOT_SPEC_SCHEMA.md for field definitions
shots:
  - id: S01
    duration: 6
    tier: lite
    tags: [ambient-transitional]
    composition: "..."
    camera: "slow push-in"
    mood: "warm invitation"
    reference_pages: null             # greenfield — no existing IP
    page_text_overlay: null
    vo_line: null
    motion_source: veo
    audio_note: "music only, gentle fade-in"
    characters: []
    setting: pastoral-meadow
    action: "Camera slowly approaches the meadow at golden hour"
    handoff_from: null
    handoff_to: S02
```

## Production notes

- **Budget allocation** — target {X} Veo Standard, {Y} Veo Fast, {Z} Veo Lite clips.
- **Ken-Burns budget** — target ≤ 20% of shots (D032); only `ambient-transitional` + `final-deliverable` tags eligible.
- **Regeneration budget** — 1 regen per character-critical shot, 0 for final-deliverable.
- **VO timing** — per Whisper segment timestamps from `audio_transcript.json`. See D042.

## Dependencies

- Characters referenced: {list from CHARACTER_SHEET.md}
- Settings used: {list, must all be in STYLE_BIBLE.md setting vocabulary}
- Fonts for overlays: {from font_identification.json or STYLE_BIBLE.md}
