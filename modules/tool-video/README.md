# tool-video

Amplifier tool module that wraps **Google Veo 3.1** video generation.  
Lives in `amplifier-bundle-creative/modules/tool-video/`.

---

## What this module does

Exposes two Amplifier tools:

| Tool | Purpose |
|------|---------|
| `generate_video` | Submit a first-frame-anchored video to Veo 3.1, poll until done, write `.mp4` |
| `list_video_models` | Return the static Veo tier/capability catalog (valid tiers, durations, resolutions) |

---

## D033 validation behaviour

Every `generate_video` call is validated against the **D033 tier × duration matrix
before any API request is made**, so no quota is burned on guaranteed-to-fail inputs.

| Tier | Allowed `duration_s` | Notes |
|------|---------------------|-------|
| `lite` | 4, 5, 6 | Short-form / social content |
| `fast` | 8 | Speed-optimised render |
| `standard` | 8 | Higher-quality render (recommended default) |

Invalid combinations raise `VeoTierMismatch` with an explicit D033 citation.  
Unknown tier names raise `ValueError`.

---

## Exception hierarchy

All Veo exceptions inherit `VeoError`, so callers can do blanket catches while
still routing specific cases:

```
VeoError
├── VeoQuotaExhausted(retry_after_s)   — 429 after all retries
├── VeoTierMismatch(tier, duration, expected)  — D033 violation
├── VeoTimeout(elapsed_s)              — polling exceeded limit
└── VeoAPIError(status_code, message)  — other API errors
```

---

## Ken-Burns fallback design decision

**This tool does NOT implement Ken-Burns fallback.** When `VeoQuotaExhausted`
fires (quota fully exhausted after 30s / 60s / 120s retries), the tool raises
and returns a structured `ToolResult` with `"agent_action": "route_to_ken_burns_fallback"`.

The **video-generator agent** decides what to do next: generate a Ken-Burns
animation from stills, queue the request for a later retry, or abort.

This is intentional separation of concerns — the tool does one job (Veo
submission + polling) and gets out of the way when quota fails.

For the forensic backstory on this decision, see `spec/DECISIONS.md`.

---

## Credential resolution

`GEMINI_API_KEY` is resolved in this order:

1. `gemini_api_key` parameter on the tool call (explicit per-call override)
2. `GEMINI_API_KEY` or `GOOGLE_API_KEY` environment variable
3. `~/.amplifier/settings.yaml` — first `AIza...` match

---

## Usage from a behavior YAML

```yaml
tools:
  - module: tool-video
    source: ./modules/tool-video
```

---

## Quick pseudocode (video-generator agent usage)

```python
# 1. Check valid combos
result = await tools["list_video_models"].execute({})
# -> [{tier: "standard", max_duration_s: 8, ...}, ...]

# 2. Generate
result = await tools["generate_video"].execute({
    "prompt": "A golden retriever running on a beach, slow motion",
    "first_frame_path": "/tmp/frame_001.jpg",
    "tier": "standard",
    "duration_s": 8,
    "aspect_ratio": "16:9",
    "resolution": "1080p",
    "output_path": "~/Videos/clip.mp4",
})

if result.success:
    print(result.output["file"])          # ~/Videos/clip.mp4
    print(result.output["generation_time_s"])
elif result.error["type"] == "VeoQuotaExhausted":
    # Tool says route to Ken-Burns — agent owns this decision
    trigger_ken_burns_fallback(...)
elif result.error["type"] == "VeoTierMismatch":
    # Fix the input params and retry
    fix_params_and_retry(result.error["allowed_durations"])
```

---

## Running the validation tests

No API key needed — these are pure unit tests:

```bash
cd modules/tool-video
pip install -e ".[dev]"
pytest tests/test_validation.py -v
```

---

## TODOs / deferred work

See `spec/DECISIONS.md` for the full forensic backstory. Short list:

- **Extract to own repo** when other bundles need `tool-video`
- **Sora 2 support** (D010 — stub only; integrate when API is stable)
- **xAI Grok Video** (deferred — API not yet evaluated)
- **Edit / extend-video** (Veo 3.1 preview APIs not stable enough yet)
- **Dynamic model discovery** (currently a static catalog)
