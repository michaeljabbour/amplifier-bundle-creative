# Character Sheet — {project-name}

**Author:** creative-director
**Version:** v1
**Decisions:** D028 (ref-image-first), D029 (setting-match ref selection)

## Purpose

Per-character reference-page ranking + morphology notes that `image-generator` consumes at every shot generation. This file IS the character-identity contract — drift is measured against these refs.

## Character: {name}

- **Role in story:** {one line}
- **Morphology notes:** age band, body type, face register (painterly / cartoon / photoreal), distinguishing features (glasses, hair, scars, accessories)
- **Rendering technique:** {e.g., watercolor-painterly, flat-vector, photoreal-commercial}
- **Wardrobe palette:** {colors + fabric cues — e.g., warm charcoal jumpsuit, cream accents}
- **Wardrobe rules:** {what never changes, what can vary}
- **Voice cues** (if relevant for VO direction): {one line}

### Reference-page rankings

Ranked highest to lowest. Each ranking cites setting-match category + face-clarity score (per D029 — setting first, clarity second).

| Rank | Page / image | Setting category | Face clarity | Use for |
|---:|---|---|---|---|
| 1 | `01_source/book_pages/page_07.png` | interior-desk | high | any interior/desk shot |
| 2 | `01_source/book_pages/page_11.png` | pastoral-meadow | medium | any outdoor/meadow shot |
| 3 | `01_source/book_pages/page_03.png` | abstract-gradient | high | hero close-ups |

### Setting × reference matrix

| Setting (from STYLE_BIBLE) | Preferred refs (top 3) |
|---|---|
| `interior-desk` | `page_07.png`, `page_08.png`, `page_06.png` |
| `pastoral-meadow` | `page_11.png`, `page_04.png`, `page_05.png` |
| `night-network` | `page_13.png`, `page_14.png` |
| `{other setting}` | `{refs}` |

### Forbidden combinations

- Do not use `page_XX.png` as primary ref for `{setting}` — the lighting contradicts.
- Minimum 2 refs per generation for this character.

---

## Character: {next character — repeat structure above}

---

## Fallback rules

- If a shot needs this character in a setting not listed in the matrix: fall back to the highest-ranked ref whose setting category is adjacent (e.g., `interior-library` → use `interior-desk` refs).
- If fewer than 2 refs exist for this character: halt generation; escalate to creative-director for a HANDOFF asking the operator for more reference material.
- If a scene needs multiple characters together and no ref shows them together: use the highest-ranked solo ref for each + explicit composition instructions in the prompt (no ref of a crowd scene should be invented).
