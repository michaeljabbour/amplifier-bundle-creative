"""Pydantic input schemas for the tool-video tools.

Each schema maps 1-to-1 to a tool's input_schema. Pydantic validates
the input dict before it reaches any API call, giving callers rich
validation errors instead of obscure SDK exceptions.

Usage:
    from .schemas import GenerateVideoInput
    parsed = GenerateVideoInput.model_validate(input_dict)
    # parsed.tier, parsed.duration_s, etc. are typed and validated
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class GenerateVideoInput(BaseModel):
    """Validated input for the generate_video tool.

    The (tier, duration_s) pair is further validated by validation.py
    per D033 after Pydantic runs — Pydantic catches type/range errors,
    D033 validation catches invalid cross-field combinations.
    """

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description=(
            "Text description of the desired video. "
            "Be specific: subject, action, camera movement, lighting, mood. "
            "1–4000 characters."
        ),
    )

    first_frame_path: str = Field(
        ...,
        description=(
            "Absolute or ~-expanded path to a JPEG/PNG/WebP image that "
            "anchors the first frame of the generated video. "
            "The file must exist on disk before calling this tool."
        ),
    )

    tier: Literal["lite", "fast", "standard"] = Field(
        ...,
        description=(
            "Veo rendering tier. Controls the quality / speed trade-off. "
            "'lite' → 4–6 s clips, fast render. "
            "'fast' → 8 s, speed-optimised. "
            "'standard' → 8 s, higher-quality render. "
            "Call list_video_models for full tier capabilities."
        ),
    )

    duration_s: int = Field(
        ...,
        ge=4,
        le=8,
        description=(
            "Video duration in seconds. Must be valid for the selected tier "
            "per D033 (lite: 4–6, fast: 8, standard: 8). "
            "Invalid combinations are rejected before any API call."
        ),
    )

    aspect_ratio: Literal["16:9", "9:16", "1:1"] = Field(
        default="16:9",
        description=(
            "Output aspect ratio. "
            "'16:9' = landscape (default), '9:16' = portrait / vertical, "
            "'1:1' = square."
        ),
    )

    resolution: Literal["720p", "1080p"] = Field(
        default="1080p",
        description=(
            "Output resolution. '1080p' recommended unless bandwidth is a concern. "
            "Use list_video_models to check per-tier support."
        ),
    )

    output_path: str = Field(
        ...,
        description=(
            "Filesystem path where the generated .mp4 will be written. "
            "Parent directories are created automatically. "
            "Supports ~ expansion."
        ),
    )

    gemini_api_key: str | None = Field(
        default=None,
        description=(
            "Optional Gemini API key override. "
            "Falls back to GEMINI_API_KEY / GOOGLE_API_KEY env vars, "
            "then ~/.amplifier/settings.yaml."
        ),
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "prompt": "A golden retriever running along a sun-drenched beach, slow motion",
                "first_frame_path": "/tmp/frames/frame_001.jpg",
                "tier": "standard",
                "duration_s": 8,
                "aspect_ratio": "16:9",
                "resolution": "1080p",
                "output_path": "~/Videos/output.mp4",
            }
        }
    }


class ListVideoModelsInput(BaseModel):
    """Input schema for list_video_models (no required fields)."""

    model_config = {"json_schema_extra": {"example": {}}}
