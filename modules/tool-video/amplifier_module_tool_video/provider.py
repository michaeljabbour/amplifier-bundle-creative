"""Veo API provider for tool-video.

Wraps the google-genai SDK for video generation. This module has no
knowledge of Amplifier internals — it is a pure async function that
takes a validated parameter set and returns a result dict or raises a
typed VeoError subclass.

Designed around the same google-genai lazy-import pattern used by
imagen-mcp's GeminiProvider (src/providers/gemini_provider.py), but
adapted for the video generation API instead of the image API.

Key decisions embedded here:
- D030: Explicit timeout=180s on all long-running calls
- No Ken-Burns fallback — that is the CALLER'S (agent's) responsibility
- Supports both inline_data (video_bytes) and URI response shapes
- 429 retry: 30s / 60s / 120s then raises VeoQuotaExhausted
- Per-call API key resolution: input > GEMINI_API_KEY env > settings.yaml
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
import time
from functools import partial
from pathlib import Path
from typing import Any

import httpx

from .validation import (
    VALID_COMBINATIONS,
    VeoAPIError,
    VeoQuotaExhausted,
    VeoTierMismatch,
    VeoTimeout,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Default Veo model — same identifier for all tiers at 3.1 launch;
# update TIER_MODELS when Google releases tier-specific endpoints.
VEO_MODEL = "veo-3.1-generate-preview"

# Polling per D030 principle (long operations need explicit timeouts)
POLL_INTERVAL_S: int = 10
POLL_MAX_ATTEMPTS: int = 60  # 60 × 10s = 10-minute maximum poll window

# Per D030 — long operations need explicit timeouts; 180 s matches MCP defaults
REQUEST_TIMEOUT_S: int = 180

# Backoff ladder for 429 / RESOURCE_EXHAUSTED
# After the initial attempt we wait 30s, then 60s, then 120s; 4th failure → raise
QUOTA_RETRY_BACKOFFS: list[int] = [30, 60, 120]

# Tier → Veo model identifier map (currently all the same; kept for future
# divergence when lite/fast/standard get separate model endpoints)
TIER_MODELS: dict[str, str] = {
    "lite": VEO_MODEL,
    "fast": VEO_MODEL,
    "standard": VEO_MODEL,
}

# Static catalog returned by list_video_models tool
VIDEO_MODELS_CATALOG: list[dict[str, Any]] = [
    {
        "tier": "lite",
        "model": VEO_MODEL,
        "min_duration_s": 4,
        "max_duration_s": 6,
        "supports_1080p": True,
        "notes": "4–6 s clips; fastest render; good for short-form / social content",
    },
    {
        "tier": "fast",
        "model": VEO_MODEL,
        "min_duration_s": 8,
        "max_duration_s": 8,
        "supports_1080p": True,
        "notes": "8 s; speed-optimised render path",
    },
    {
        "tier": "standard",
        "model": VEO_MODEL,
        "min_duration_s": 8,
        "max_duration_s": 8,
        "supports_1080p": True,
        "notes": "8 s; higher-quality render; recommended default for hero content",
    },
]

# ---------------------------------------------------------------------------
# Credential resolution
# ---------------------------------------------------------------------------


def _load_key_from_settings_yaml() -> str | None:
    """Walk ~/.amplifier/settings.yaml for an AIza... API key string.

    Matches the credential-discovery pattern from imagen-mcp: search for
    the canonical Google API key prefix (AIza) without requiring the YAML
    to have a specific structure. Returns the first match found.
    """
    settings_path = Path.home() / ".amplifier" / "settings.yaml"
    if not settings_path.exists():
        return None
    try:
        content = settings_path.read_text(encoding="utf-8")
        # Google API keys: "AIza" followed by exactly 35 alphanumeric / dash / underscore chars
        matches = re.findall(r"AIza[0-9A-Za-z_-]{35}", content)
        if matches:
            logger.debug("Resolved Gemini API key from ~/.amplifier/settings.yaml")
            return matches[0]
    except OSError as exc:
        logger.debug("Could not read ~/.amplifier/settings.yaml: %s", exc)
    return None


def resolve_api_key(provided_key: str | None = None) -> str:
    """Resolve the Gemini API key using a three-tier priority chain.

    Priority:
      1. ``provided_key`` — explicit per-call override
      2. ``GEMINI_API_KEY`` env var (also accepts ``GOOGLE_API_KEY``)
      3. ``~/.amplifier/settings.yaml`` — first ``AIza...`` match

    Args:
        provided_key: Optional explicit key from the tool input.

    Returns:
        Resolved API key string.

    Raises:
        ValueError: If no key can be resolved from any source.
    """
    if provided_key:
        return provided_key

    env_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if env_key:
        return env_key

    yaml_key = _load_key_from_settings_yaml()
    if yaml_key:
        return yaml_key

    raise ValueError(
        "Gemini API key not found. Provide it via one of: "
        "(1) gemini_api_key tool parameter, "
        "(2) GEMINI_API_KEY environment variable, or "
        "(3) ~/.amplifier/settings.yaml"
    )


# ---------------------------------------------------------------------------
# SDK lazy import (mirrors imagen-mcp pattern)
# ---------------------------------------------------------------------------

genai: Any = None
types: Any = None


def _import_genai() -> None:
    """Lazily import google-genai SDK to avoid hard failure at module load.

    This mirrors the pattern in imagen-mcp's GeminiProvider: defer the
    import so the module can be loaded (and tested) without the SDK
    installed, failing only at generation time.
    """
    global genai, types  # noqa: PLW0603
    if genai is None:
        try:
            from google import genai as _genai  # type: ignore[attr-defined]
            from google.genai import types as _types  # type: ignore[import-untyped]

            genai = _genai
            types = _types
        except ImportError as exc:
            raise ImportError(
                "tool-video requires the 'google-genai' package (>=0.3). "
                "Install with: pip install 'google-genai>=0.3'"
            ) from exc


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def generate_video(
    *,
    prompt: str,
    first_frame_path: str,
    tier: str,
    duration_s: int,
    aspect_ratio: str,
    resolution: str,
    output_path: str,
    gemini_api_key: str | None = None,
) -> dict[str, Any]:
    """Submit a Veo video generation request and poll until complete.

    Caller must have already run ``validation.validate(tier, duration_s)``
    before calling this function. This function does NOT re-run D033
    validation — that is intentional separation of concerns.

    Args:
        prompt:          Text description of the desired video.
        first_frame_path: Path to the first-frame anchor image (must exist).
        tier:            "lite", "fast", or "standard".
        duration_s:      Video duration in seconds (pre-validated by caller).
        aspect_ratio:    "16:9", "9:16", or "1:1".
        resolution:      "720p" or "1080p".
        output_path:     Filesystem path to write the resulting .mp4.
        gemini_api_key:  Optional API key override.

    Returns:
        dict with keys: file, size_bytes, duration_s, tier, model,
        provider, generation_time_s

    Raises:
        FileNotFoundError:  If first_frame_path does not exist on disk.
        ValueError:         If credentials cannot be resolved.
        VeoQuotaExhausted:  After 429 retries are exhausted.
        VeoTierMismatch:    If API returns 400 with tier/duration language.
        VeoTimeout:         If polling exceeds POLL_MAX_ATTEMPTS * POLL_INTERVAL_S.
        VeoAPIError:        For other API errors.
    """
    _import_genai()

    # Validate first-frame exists on disk
    frame_path = Path(first_frame_path).expanduser().resolve()
    if not frame_path.exists():
        raise FileNotFoundError(
            f"first_frame_path not found: {frame_path}. "
            "The file must exist on disk before calling generate_video."
        )

    # Resolve credentials
    api_key = resolve_api_key(gemini_api_key)

    model_id = TIER_MODELS.get(tier, VEO_MODEL)
    start_time = time.monotonic()

    # Submit with quota-retry logic
    operation = await _submit_with_retry(
        api_key=api_key,
        model_id=model_id,
        prompt=prompt,
        frame_path=frame_path,
        duration_s=duration_s,
        aspect_ratio=aspect_ratio,
        resolution=resolution,
        tier=tier,
    )

    # Poll until done
    operation = await _poll_until_done(api_key=api_key, operation=operation)

    # Extract video bytes (handles inline_data and URI shapes)
    video_bytes = await _extract_video_bytes(operation)

    # Write mp4 to output_path
    out_path = Path(output_path).expanduser()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(video_bytes)

    elapsed = time.monotonic() - start_time

    logger.info(
        "Video generated: tier=%s duration=%ds size=%d bytes path=%s elapsed=%.1fs",
        tier,
        duration_s,
        len(video_bytes),
        out_path,
        elapsed,
    )

    return {
        "file": str(out_path),
        "size_bytes": len(video_bytes),
        "duration_s": float(duration_s),
        "tier": tier,
        "model": model_id,
        "provider": "google",
        "generation_time_s": round(elapsed, 2),
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


async def _submit_with_retry(
    *,
    api_key: str,
    model_id: str,
    prompt: str,
    frame_path: Path,
    duration_s: int,
    aspect_ratio: str,
    resolution: str,
    tier: str,
) -> Any:
    """Submit the Veo generation request with quota-retry logic.

    Retries up to ``len(QUOTA_RETRY_BACKOFFS)`` times on
    429 / RESOURCE_EXHAUSTED with increasing wait times.

    Raises:
        VeoQuotaExhausted:  If all retries are exhausted.
        VeoTierMismatch:    If the API returns 400 with tier/duration language.
        VeoAPIError:        For other non-retryable API errors.
    """
    client = genai.Client(api_key=api_key)

    # Read first-frame bytes (small enough to hold in memory)
    image_bytes = frame_path.read_bytes()

    # Detect MIME type from file extension
    suffix = frame_path.suffix.lower()
    mime_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }
    mime_type = mime_map.get(suffix, "image/jpeg")

    last_exc: Exception | None = None
    backoffs = [0] + QUOTA_RETRY_BACKOFFS  # [no-wait, 30s, 60s, 120s]

    for attempt, backoff in enumerate(backoffs):
        if backoff > 0:
            logger.warning(
                "Veo quota limit hit (attempt %d/%d). Waiting %ds before retry.",
                attempt,
                len(backoffs),
                backoff,
            )
            await asyncio.sleep(backoff)

        try:
            loop = asyncio.get_running_loop()
            operation = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    partial(
                        _sync_submit,
                        client=client,
                        model_id=model_id,
                        prompt=prompt,
                        image_bytes=image_bytes,
                        mime_type=mime_type,
                        duration_s=duration_s,
                        aspect_ratio=aspect_ratio,
                        resolution=resolution,
                    ),
                ),
                timeout=REQUEST_TIMEOUT_S,  # D030 explicit timeout
            )
            return operation

        except Exception as exc:
            exc_str = str(exc).lower()

            # 429 / quota exhausted → retry with backoff
            if _is_quota_error(exc_str):
                last_exc = exc
                retry_after = _parse_retry_after(exc_str)
                if attempt < len(backoffs) - 1:
                    # More retries left; continue to next iteration
                    continue
                # All retries exhausted
                raise VeoQuotaExhausted(retry_after_s=retry_after) from exc

            # 400 / INVALID_ARGUMENT → check for tier/duration mismatch language
            if _is_invalid_argument(exc_str):
                if _mentions_tier_or_duration(exc_str):
                    allowed = VALID_COMBINATIONS.get(tier, set())
                    raise VeoTierMismatch(tier=tier, duration=duration_s, expected=allowed) from exc
                raise VeoAPIError(status_code=400, message=str(exc)) from exc

            # Everything else: surface as VeoAPIError
            raise VeoAPIError(status_code=0, message=str(exc)) from exc

    # Should be unreachable; satisfies the type checker
    raise VeoQuotaExhausted() from last_exc


def _sync_submit(
    *,
    client: Any,
    model_id: str,
    prompt: str,
    image_bytes: bytes,
    mime_type: str,
    duration_s: int,
    aspect_ratio: str,
    resolution: str,
) -> Any:
    """Synchronous Veo submission (runs inside run_in_executor)."""
    image = types.Image(image_bytes=image_bytes, mime_type=mime_type)

    config = types.GenerateVideosConfig(
        aspect_ratio=aspect_ratio,
        duration_seconds=duration_s,
        resolution=resolution,
        number_of_videos=1,
    )

    return client.models.generate_videos(
        model=model_id,
        prompt=prompt,
        image=image,
        config=config,
    )


async def _poll_until_done(*, api_key: str, operation: Any) -> Any:
    """Poll the Veo operation until it is done or timeout is reached.

    Uses POLL_INTERVAL_S between checks and gives up after
    POLL_MAX_ATTEMPTS attempts (default: 10 minutes).

    Raises:
        VeoTimeout: If polling exceeds the limit.
    """
    client = genai.Client(api_key=api_key)
    loop = asyncio.get_running_loop()
    attempts = 0

    while not operation.done:
        if attempts >= POLL_MAX_ATTEMPTS:
            elapsed_s = attempts * POLL_INTERVAL_S
            raise VeoTimeout(elapsed_s=elapsed_s)

        await asyncio.sleep(POLL_INTERVAL_S)
        attempts += 1

        try:
            operation = await loop.run_in_executor(
                None,
                partial(client.operations.get, operation),
            )
        except Exception as exc:
            # Transient poll failure — log and keep trying until VeoTimeout fires
            logger.warning(
                "Poll attempt %d/%d failed (will retry): %s",
                attempts,
                POLL_MAX_ATTEMPTS,
                exc,
            )

    return operation


async def _extract_video_bytes(operation: Any) -> bytes:
    """Extract video bytes from a completed Veo operation response.

    Handles both response shapes returned by the Veo API:
    - ``inline_data``: video_bytes is directly attached to the response object
    - ``uri``:         a signed URL that must be downloaded via httpx

    Raises:
        VeoAPIError: If neither video_bytes nor uri is present in the response.
    """
    try:
        video = operation.response.generated_videos[0].video
    except (AttributeError, IndexError, TypeError) as exc:
        raise VeoAPIError(
            status_code=0,
            message=f"Could not extract video from operation response: {exc}",
        ) from exc

    # Shape 1: inline bytes (small clips or when SDK has already buffered)
    video_bytes = getattr(video, "video_bytes", None)
    if video_bytes:
        logger.debug("Video delivered as inline bytes (%d bytes)", len(video_bytes))
        return bytes(video_bytes)

    # Shape 2: signed URI (Veo typically uses this for larger / longer clips)
    uri = getattr(video, "uri", None)
    if uri:
        logger.debug("Video delivered as signed URI, downloading: %s", uri[:80])
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as http:
            resp = await http.get(uri)
            resp.raise_for_status()
            return resp.content

    raise VeoAPIError(
        status_code=0,
        message=(
            "Veo operation response contained neither video_bytes nor uri. "
            "This may indicate a model error or an unsupported SDK version."
        ),
    )


# ---------------------------------------------------------------------------
# Error classification helpers
# ---------------------------------------------------------------------------


def _is_quota_error(exc_str: str) -> bool:
    """Return True if the error string looks like a quota/rate-limit error."""
    return any(
        token in exc_str
        for token in (
            "429",
            "resource_exhausted",
            "quota_exceeded",
            "rate_limit",
            "rateLimitExceeded",
        )
    )


def _is_invalid_argument(exc_str: str) -> bool:
    """Return True if the error string looks like a bad-argument error."""
    return "400" in exc_str or "invalid_argument" in exc_str


def _mentions_tier_or_duration(exc_str: str) -> bool:
    """Return True if the error text references tier or duration fields."""
    return any(token in exc_str for token in ("duration", "tier", "model", "parameter", "config"))


def _parse_retry_after(exc_str: str) -> int | None:
    """Extract a retry-after hint (seconds) from an error string, if present."""
    match = re.search(r"retry[_\s-]?after[:\s]+(\d+)", exc_str)
    return int(match.group(1)) if match else None
