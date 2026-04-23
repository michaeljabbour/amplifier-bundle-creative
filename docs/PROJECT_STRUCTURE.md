# Creative Bundle — Film Production Project Structure

**Status:** Active template. Every creative project produced with this bundle should follow this layout.

This is not arbitrary file organization. It is film-production discipline applied to AI-generated animation projects. The operator should be able to navigate the project dir like walking through a studio: source material in one wing, pre-production in another, dailies in a third, final masters on the shelf.

---

## The layout

```
{project-name}-{YYYYMMDD-HHmmss}/
├── README.md                      # Project header — what this is, who owns it, what's where
│
├── 01_source/                     # OPERATOR-SUPPLIED inputs (read-only)
│   ├── book_pages/                # If reproducing existing IP, source page scans (symlinked)
│   ├── *.wav / *.mp3              # Music / audio tracks provided by operator
│   └── *.md                       # Any briefs, notes, style references the operator provides
│
├── 02_preproduction/              # DISCOVERY + PLANNING artifacts
│   ├── book_text_extracted.json   # Vision-extracted verbatim page text (D037)
│   ├── font_identification.json   # Multi-sample font ID report (D037)
│   ├── CHARACTER_SHEET.md         # Snapshot of character reference doc
│   ├── SHOT_LIST*.md              # Snapshot of shot list(s) used for this production
│   └── STYLE_BIBLE.md             # Snapshot of style bible
│
├── 03_shots/                      # PER-SHOT generated assets
│   ├── frames/                    # Nano Banana Pro first frames (PNG per shot)
│   └── motion/                    # Veo 3.1 or Ken-Burns motion clips (MP4 per shot)
│
├── 04_audio/                      # AUDIO pipeline
│   ├── narration/v1/              # First pass of narration (kept for forensics)
│   ├── narration/v2/              # Second pass if any (kept for forensics)
│   ├── narration/vN/              # Current / latest narration
│   ├── music/                     # Symlinks to 01_source/ music files
│   └── tracks/                    # Built intermediate tracks (VO concat, music+VO combined)
│
├── 05_titles/                     # Text overlay PNGs (page-verbatim text per D035)
│   └── vN/                        # Version-subfoldered if iterating
│
├── 06_masters/                    # DELIVERABLES — final masters
│   ├── v1_silent.mp4 / v1_clean.mp4 / v1_titled.mp4
│   ├── v2_silent.mp4 / v2_clean.mp4 / v2_titled.mp4
│   └── vN_silent.mp4 / vN_clean.mp4 / vN_titled.mp4
│   (Keep all versions for operator comparison. Archive only after new version is approved.)
│
├── 07_logs/                       # EVENT LOGS from generation pipeline
│   ├── batch_*.jsonl              # Per-batch event streams (D036-style raw audit trail)
│   └── *.stdout / *.stderr        # Captured stdout/stderr from background jobs
│
├── 08_qa/                         # QA REPORTS + manifests
│   ├── vN_manifest.json           # Production manifest (settings + durations + file map)
│   └── *_summary.json             # Batch summaries with shot-level outcomes
│
├── 99_archive/                    # SUPERSEDED artifacts (kept for forensics)
│   ├── v1_*.mp4                   # Old masters once superseded
│   ├── _vo_track_v{1-3}.m4a       # Broken-then-fixed intermediate tracks
│   └── */                         # Temp work dirs from prior runs
│
└── scripts/                       # All PYTHON production scripts
    ├── batch_*_production.py      # Generation scripts
    ├── retry_failed.py            # Quota/error retry logic
    ├── extract_text_and_font.py   # Pre-production discovery scripts
    ├── rebuild_vo_vN.py           # VO pipeline iterations
    ├── produce_vN.py              # Full-production pipeline scripts
    └── ...
```

## The discipline

### What goes where, in one sentence each

- **01_source** — read-only operator inputs. If the operator says "use *their* music track," it lives here. If you reproduce an existing book, the source pages live here (symlinked from `~/Downloads/` or wherever they arrived). You never write derived files into `01_source/`.
- **02_preproduction** — everything discovered before generation: book text extraction, font ID, character sheet snapshots, shot list snapshots. If it's about understanding the piece before building it, it lives here.
- **03_shots** — per-shot artifacts. Two flat subdirs: `frames/` (PNG) and `motion/` (MP4). Nothing else. One file per shot. Named `shotNN_frame.png` / `shotNN_motion.mp4`.
- **04_audio** — audio pipeline. Narration organized by version (v1, v2, vN). Music symlinks. Built tracks (VO concat, music+VO) in `tracks/`.
- **05_titles** — text overlay PNGs, optionally version-subfoldered.
- **06_masters** — deliverables. Always `{version}_silent.mp4` + `{version}_clean.mp4` + `{version}_titled.mp4`. Keep all versions for operator comparison.
- **07_logs** — raw event logs. Don't delete these; they're forensic evidence if anything goes wrong later.
- **08_qa** — QA reports + manifests. The manifest for a version is the authoritative record of what settings produced that master.
- **99_archive** — superseded or failed intermediates. Kept until the project is shipped and archived.
- **scripts** — all Python that ran during production, named by purpose and version.

### Rules

1. **Numeric prefixes enforce pipeline ordering.** You read 01 → 02 → 03 → … → 06 deliverables. A file in `05_titles/` should never need to reach back into `06_masters/` — it's upstream in the pipeline.
2. **Version every iteration in `06_masters/`.** Don't overwrite the operator's v2 with v3. Keep v2 visible so the operator can compare. Move to `99_archive/` only after explicit approval.
3. **`99_archive/` is not a trash can.** It's the forensic record. Move things there when they're superseded; do not delete.
4. **Symlinks are fine for heavy source data.** Don't copy 200 MB of book page scans into `01_source/book_pages/` — symlink them.
5. **Scripts are versioned by purpose, not date.** `produce_v2.py`, `produce_v3.py`, `rebuild_vo_v4.py`. Never `produce_20260422.py`.
6. **`README.md` at the project root** tells the operator the story: what this project is, what's in each top-level folder, what's the current latest version in `06_masters/`.

### Why this matters

A messy run dir with 149 files at the root (as the pilot project dir briefly was between v1 and v2) forces the operator to do the producer's job of remembering which file is which. A film-production layout lets the operator navigate by intuition:

- "Where's the music?" → `01_source/`
- "Where's the final cut?" → `06_masters/`
- "Why did shot 20 fail?" → `07_logs/`
- "What font did we use?" → `02_preproduction/font_identification.json`
- "Can I compare v2 and v3?" → Both are in `06_masters/`
- "What was the v3 audio mix?" → `08_qa/v3_manifest.json`

The operator shouldn't have to ask the AI. The folder structure answers.

### Applying this to new projects

The bundle's post-production toolkit (phase 2b) should provide a `init_project_dir(project_name: str, output_root: Path) -> Path` helper that creates this full structure with placeholder READMEs in each subdir explaining what goes there. Every subsequent pipeline step (batch production, VO generation, stitching, overlays) writes to the right numbered subdir by convention.

This is encoded in D039.
