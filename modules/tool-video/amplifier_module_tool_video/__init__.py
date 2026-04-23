"""Amplifier tool module: tool-video.

Wraps Google Veo 3.1 video generation as two Amplifier tools:
  - generate_video:     Submit a first-frame-anchored video generation request
  - list_video_models:  Return the static Veo tier/capability catalog

mount() pattern mirrors amplifier-bundle-recipes/modules/tool-recipes/:
  - Takes (coordinator, config)
  - Registers tools into coordinator.mount_points["tools"]
  - Returns a metadata dict (per creating-amplifier-modules skill)

Design decisions baked in here:
  - D033: (tier, duration_s) validated BEFORE API submission
  - D030: Explicit 180s timeout on all long operations
  - No Ken-Burns fallback in this tool — agents own that recovery path
  - Typed exceptions let callers route recovery without string-matching
"""

from __future__ import annotations

import logging
from typing import Any

from .provider import VIDEO_MODELS_CATALOG, generate_video
from .schemas import GenerateVideoInput, ListVideoModelsInput
from .validation import VeoError, VeoQuotaExhausted, VeoTierMismatch, validate

logger = logging.getLogger(__name__)

# Lazy import for amplifier_core — it is a peer dependency that is always
# present at runtime but may not be installed in test environments that only
# exercise validation logic. We provide a minimal shim so those tests pass.
try:
    from amplifier_core import ToolResult  # type: ignore[import-untyped]
except ImportError:
    from dataclasses import dataclass

    @dataclass  # type: ignore[no-redef]
    class ToolResult:  # type: ignore[no-redef]
        """Minimal ToolResult shim for environments without amplifier-core."""

        success: bool
        output: Any = None
        error: dict[str, Any] | None = None


# ---------------------------------------------------------------------------
# Tool: generate_video
# ---------------------------------------------------------------------------


class GenerateVideoTool:
    """Submit a first-frame-anchored video to Google Veo 3.1 and wait for it.

    This tool:
    - Validates (tier, duration_s) per D033 before any API call
    - Polls until the operation completes (up to 10 minutes)
    - Handles 429 quota errors with 30s/60s/120s backoff
    - Raises typed VeoError subclasses — callers route recovery

    Ken-Burns fallback lives in the agent (video-generator), NOT here.
    """

    @property
    def name(self) -> str:
        return "generate_video"

    @property
    def description(self) -> str:
        return """Generate a video from a first-frame image using Google Veo 3.1.

Validates the (tier, duration_s) pair per D033 rules BEFORE submitting to the API:
  - lite:     4, 5, or 6 seconds
  - fast:     8 seconds only
  - standard: 8 seconds only

On 429 RESOURCE_EXHAUSTED, retries with 30s / 60s / 120s backoff.
If all retries fail, raises VeoQuotaExhausted — the CALLER is responsible
for Ken-Burns fallback or other recovery (this tool does not fall back itself).

Returns: {file, size_bytes, duration_s, tier, model, provider, generation_time_s}"""

    @property
    def input_schema(self) -> dict[str, Any]:
        return GenerateVideoInput.model_json_schema()

    async def execute(self, input: dict[str, Any]) -> ToolResult:  # noqa: A002
        """Execute video generation.

        Args:
            input: Dict matching GenerateVideoInput schema.

        Returns:
            ToolResult with output dict on success, error dict on failure.
        """
        # Pydantic validation first (type checking, range checking, required fields)
        try:
            params = GenerateVideoInput.model_validate(input)
        except Exception as exc:
            return ToolResult(
                success=False,
                error={"type": "ValidationError", "message": str(exc)},
            )

        # D033 pre-flight check — reject before burning quota
        try:
            validate(params.tier, params.duration_s)
        except VeoTierMismatch as exc:
            return ToolResult(
                success=False,
                error={
                    "type": "VeoTierMismatch",
                    "message": str(exc),
                    "tier": exc.tier,
                    "duration_s": exc.duration,
                    "allowed_durations": sorted(exc.expected),
                    "citation": "D033 — see spec/DECISIONS.md",
                },
            )
        except ValueError as exc:
            return ToolResult(
                success=False,
                error={"type": "ValueError", "message": str(exc)},
            )

        # Submit to Veo API
        try:
            result = await generate_video(
                prompt=params.prompt,
                first_frame_path=params.first_frame_path,
                tier=params.tier,
                duration_s=params.duration_s,
                aspect_ratio=params.aspect_ratio,
                resolution=params.resolution,
                output_path=params.output_path,
                gemini_api_key=params.gemini_api_key,
            )
            return ToolResult(success=True, output=result)

        except VeoQuotaExhausted as exc:
            # Do NOT catch and swallow — re-raise as a structured ToolResult
            # so the video-generator agent can route to Ken-Burns fallback.
            return ToolResult(
                success=False,
                error={
                    "type": "VeoQuotaExhausted",
                    "message": str(exc),
                    "retry_after_s": exc.retry_after_s,
                    "agent_action": "route_to_ken_burns_fallback",
                },
            )

        except VeoTierMismatch as exc:
            # Tier mismatch detected by the API (post-submission 400)
            return ToolResult(
                success=False,
                error={
                    "type": "VeoTierMismatch",
                    "message": str(exc),
                    "tier": exc.tier,
                    "duration_s": exc.duration,
                    "allowed_durations": sorted(exc.expected),
                    "citation": "D033",
                },
            )

        except VeoError as exc:
            # VeoTimeout, VeoAPIError, or any other typed subclass
            return ToolResult(
                success=False,
                error={
                    "type": type(exc).__name__,
                    "message": str(exc),
                },
            )

        except FileNotFoundError as exc:
            return ToolResult(
                success=False,
                error={"type": "FileNotFoundError", "message": str(exc)},
            )

        except Exception as exc:
            logger.exception("Unexpected error in generate_video")
            return ToolResult(
                success=False,
                error={
                    "type": type(exc).__name__,
                    "message": str(exc),
                },
            )


# ---------------------------------------------------------------------------
# Tool: list_video_models
# ---------------------------------------------------------------------------


class ListVideoModelsTool:
    """Return the static catalog of available Veo tiers and their capabilities.

    This is a static list. Dynamic model discovery is a future TODO.
    Useful for callers that need to know which (tier, duration_s) combos
    are valid before building a generate_video call.
    """

    @property
    def name(self) -> str:
        return "list_video_models"

    @property
    def description(self) -> str:
        return """Return the available Veo video generation tiers and their capabilities.

Returns a list of tier descriptors:
  [{tier, model, min_duration_s, max_duration_s, supports_1080p, notes}, ...]

Use this before generate_video to discover valid (tier, duration_s) combinations.
The D033 validation matrix is enforced server-side by generate_video."""

    @property
    def input_schema(self) -> dict[str, Any]:
        return ListVideoModelsInput.model_json_schema()

    async def execute(self, input: dict[str, Any]) -> ToolResult:  # noqa: A002
        """Return the static tier catalog.

        Args:
            input: Empty dict (no params required).

        Returns:
            ToolResult with list of tier descriptors.
        """
        return ToolResult(
            success=True,
            output={"models": VIDEO_MODELS_CATALOG, "count": len(VIDEO_MODELS_CATALOG)},
        )


# ---------------------------------------------------------------------------
# mount() — Amplifier module entry point
# ---------------------------------------------------------------------------


async def mount(coordinator: Any, config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Mount the tool-video module into the Amplifier coordinator.

    Registers two tools:
    - generate_video:    Veo 3.1 video generation (D033-validated)
    - list_video_models: Static tier capability catalog

    Args:
        coordinator: Amplifier ModuleCoordinator instance.
        config:      Optional module configuration dict (currently unused;
                     reserved for future per-bundle credential overrides).

    Returns:
        Metadata dict: {name, version, provides}

    NOTE on mount() signature deviation:
        The original spec described mount(config) -> dict.
        The ACTUAL Amplifier protocol (per tool-recipes canonical reference)
        is async mount(coordinator, config) with direct registration into
        coordinator.mount_points["tools"]. This implementation follows the
        canonical reference.
    """
    config = config or {}

    generate_video_tool = GenerateVideoTool()
    list_video_models_tool = ListVideoModelsTool()

    coordinator.mount_points["tools"][generate_video_tool.name] = generate_video_tool
    coordinator.mount_points["tools"][list_video_models_tool.name] = list_video_models_tool

    logger.info(
        "tool-video mounted: registered '%s', '%s'",
        generate_video_tool.name,
        list_video_models_tool.name,
    )

    return {
        "name": "tool-video",
        "version": "0.1.0",
        "provides": [generate_video_tool.name, list_video_models_tool.name],
    }
