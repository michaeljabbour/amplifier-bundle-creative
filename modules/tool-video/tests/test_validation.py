"""Unit tests for D033 tier × duration validation.

These tests exercise validation.py in isolation — no API calls, no SDK,
no amplifier-core required. They are fast and deterministic.

Coverage matrix:
  - Every valid (tier, duration_s) combination passes silently
  - Every known tier with an invalid duration raises VeoTierMismatch
  - Unknown tier raises ValueError (not VeoTierMismatch)
  - Edge values at range boundaries are covered for "lite" tier
  - VeoTierMismatch carries the correct structured attributes
  - VeoQuotaExhausted, VeoTimeout, VeoAPIError constructors are exercised
"""

from __future__ import annotations

import pytest
from amplifier_module_tool_video.validation import (
    KNOWN_TIERS,
    VALID_COMBINATIONS,
    VeoAPIError,
    VeoError,
    VeoQuotaExhausted,
    VeoTierMismatch,
    VeoTimeout,
    validate,
)

# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


class TestExceptionHierarchy:
    """All Veo exceptions must inherit VeoError for blanket catching."""

    def test_veo_tier_mismatch_is_veo_error(self):
        exc = VeoTierMismatch(tier="lite", duration=8, expected={4, 5, 6})
        assert isinstance(exc, VeoError)

    def test_veo_quota_exhausted_is_veo_error(self):
        exc = VeoQuotaExhausted(retry_after_s=30)
        assert isinstance(exc, VeoError)

    def test_veo_timeout_is_veo_error(self):
        exc = VeoTimeout(elapsed_s=600)
        assert isinstance(exc, VeoError)

    def test_veo_api_error_is_veo_error(self):
        exc = VeoAPIError(status_code=500, message="Internal server error")
        assert isinstance(exc, VeoError)


# ---------------------------------------------------------------------------
# VeoTierMismatch attributes
# ---------------------------------------------------------------------------


class TestVeoTierMismatchAttributes:
    """VeoTierMismatch must carry structured data so agents can route recovery."""

    def test_attributes_are_set(self):
        exc = VeoTierMismatch(tier="fast", duration=6, expected={8})
        assert exc.tier == "fast"
        assert exc.duration == 6
        assert exc.expected == {8}

    def test_message_contains_d033_citation(self):
        exc = VeoTierMismatch(tier="lite", duration=8, expected={4, 5, 6})
        assert "D033" in str(exc)

    def test_message_contains_tier_name(self):
        exc = VeoTierMismatch(tier="standard", duration=5, expected={8})
        assert "standard" in str(exc)

    def test_message_contains_duration(self):
        exc = VeoTierMismatch(tier="standard", duration=5, expected={8})
        assert "5" in str(exc)

    def test_message_contains_allowed_durations(self):
        exc = VeoTierMismatch(tier="lite", duration=8, expected={4, 5, 6})
        msg = str(exc)
        # At least one of the valid durations should appear
        assert "4" in msg or "5" in msg or "6" in msg


# ---------------------------------------------------------------------------
# VeoQuotaExhausted attributes
# ---------------------------------------------------------------------------


class TestVeoQuotaExhaustedAttributes:
    def test_retry_after_set(self):
        exc = VeoQuotaExhausted(retry_after_s=120)
        assert exc.retry_after_s == 120

    def test_retry_after_none(self):
        exc = VeoQuotaExhausted()
        assert exc.retry_after_s is None

    def test_message_contains_retry_hint_when_provided(self):
        exc = VeoQuotaExhausted(retry_after_s=60)
        assert "60" in str(exc)


# ---------------------------------------------------------------------------
# VeoTimeout attributes
# ---------------------------------------------------------------------------


class TestVeoTimeoutAttributes:
    def test_elapsed_s_set(self):
        exc = VeoTimeout(elapsed_s=600)
        assert exc.elapsed_s == 600

    def test_message_contains_elapsed(self):
        exc = VeoTimeout(elapsed_s=600)
        assert "600" in str(exc)


# ---------------------------------------------------------------------------
# VeoAPIError attributes
# ---------------------------------------------------------------------------


class TestVeoAPIErrorAttributes:
    def test_status_code_and_message(self):
        exc = VeoAPIError(status_code=503, message="Service Unavailable")
        assert exc.status_code == 503
        assert exc.message == "Service Unavailable"
        assert "503" in str(exc)


# ---------------------------------------------------------------------------
# VALID_COMBINATIONS matrix completeness
# ---------------------------------------------------------------------------


class TestValidCombinationsMatrix:
    """The D033 matrix must contain exactly the right tiers and values."""

    def test_known_tiers_match_valid_combinations(self):
        assert set(KNOWN_TIERS) == set(VALID_COMBINATIONS.keys())

    def test_lite_allows_4_5_6(self):
        assert VALID_COMBINATIONS["lite"] == {4, 5, 6}

    def test_fast_allows_8_only(self):
        assert VALID_COMBINATIONS["fast"] == {8}

    def test_standard_allows_8_only(self):
        assert VALID_COMBINATIONS["standard"] == {8}

    def test_all_three_tiers_present(self):
        assert "lite" in VALID_COMBINATIONS
        assert "fast" in VALID_COMBINATIONS
        assert "standard" in VALID_COMBINATIONS


# ---------------------------------------------------------------------------
# validate() — happy path (all valid combos must pass silently)
# ---------------------------------------------------------------------------


class TestValidateHappyPath:
    """Every entry in VALID_COMBINATIONS must pass validate() without raising."""

    @pytest.mark.parametrize("duration_s", [4, 5, 6])
    def test_lite_valid_durations(self, duration_s: int):
        validate("lite", duration_s)  # Must not raise

    def test_fast_valid_duration(self):
        validate("fast", 8)  # Must not raise

    def test_standard_valid_duration(self):
        validate("standard", 8)  # Must not raise

    def test_all_valid_combinations_pass(self):
        """Exhaust the entire D033 matrix — no entry should raise."""
        for tier, durations in VALID_COMBINATIONS.items():
            for duration_s in durations:
                validate(tier, duration_s)  # Must not raise for any valid combo


# ---------------------------------------------------------------------------
# validate() — D033 violation (invalid tier × duration pairs)
# ---------------------------------------------------------------------------


class TestValidateTierMismatch:
    """Invalid (tier, duration_s) pairs must raise VeoTierMismatch."""

    # --- lite violations ---

    def test_lite_rejects_duration_1(self):
        with pytest.raises(VeoTierMismatch) as exc_info:
            validate("lite", 1)
        assert exc_info.value.tier == "lite"
        assert exc_info.value.duration == 1

    def test_lite_rejects_duration_3(self):
        with pytest.raises(VeoTierMismatch):
            validate("lite", 3)

    def test_lite_rejects_duration_7(self):
        with pytest.raises(VeoTierMismatch):
            validate("lite", 7)

    def test_lite_rejects_duration_8(self):
        """8s is valid for fast/standard but NOT lite — common confusion."""
        with pytest.raises(VeoTierMismatch) as exc_info:
            validate("lite", 8)
        assert exc_info.value.tier == "lite"

    def test_lite_rejects_duration_0(self):
        with pytest.raises(VeoTierMismatch):
            validate("lite", 0)

    # --- fast violations ---

    def test_fast_rejects_duration_4(self):
        with pytest.raises(VeoTierMismatch):
            validate("fast", 4)

    def test_fast_rejects_duration_5(self):
        with pytest.raises(VeoTierMismatch):
            validate("fast", 5)

    def test_fast_rejects_duration_6(self):
        with pytest.raises(VeoTierMismatch):
            validate("fast", 6)

    def test_fast_rejects_duration_7(self):
        with pytest.raises(VeoTierMismatch):
            validate("fast", 7)

    def test_fast_rejects_duration_10(self):
        with pytest.raises(VeoTierMismatch):
            validate("fast", 10)

    # --- standard violations ---

    def test_standard_rejects_duration_4(self):
        with pytest.raises(VeoTierMismatch):
            validate("standard", 4)

    def test_standard_rejects_duration_6(self):
        with pytest.raises(VeoTierMismatch):
            validate("standard", 6)

    def test_standard_rejects_duration_10(self):
        with pytest.raises(VeoTierMismatch):
            validate("standard", 10)

    # --- error attributes on mismatch ---

    def test_tier_mismatch_carries_expected_durations(self):
        with pytest.raises(VeoTierMismatch) as exc_info:
            validate("lite", 8)
        assert exc_info.value.expected == {4, 5, 6}

    def test_tier_mismatch_carries_actual_duration(self):
        with pytest.raises(VeoTierMismatch) as exc_info:
            validate("fast", 4)
        assert exc_info.value.duration == 4

    def test_tier_mismatch_message_cites_d033(self):
        with pytest.raises(VeoTierMismatch) as exc_info:
            validate("standard", 5)
        assert "D033" in str(exc_info.value)


# ---------------------------------------------------------------------------
# validate() — unknown tier raises ValueError, not VeoTierMismatch
# ---------------------------------------------------------------------------


class TestValidateUnknownTier:
    """Unknown tier names must raise ValueError (caller's input is wrong,
    not a D033 matrix violation)."""

    def test_unknown_tier_raises_value_error(self):
        with pytest.raises(ValueError):
            validate("premium", 8)

    def test_unknown_tier_does_not_raise_veo_tier_mismatch(self):
        with pytest.raises(ValueError):
            validate("ultra", 8)

    def test_empty_tier_raises_value_error(self):
        with pytest.raises(ValueError):
            validate("", 8)

    def test_typo_tier_raises_value_error(self):
        with pytest.raises(ValueError):
            validate("Lite", 5)  # Case-sensitive — "Lite" != "lite"

    def test_value_error_mentions_known_tiers(self):
        with pytest.raises(ValueError) as exc_info:
            validate("bogus", 8)
        msg = str(exc_info.value)
        # Should mention what the valid options are
        assert "lite" in msg or "fast" in msg or "standard" in msg


# ---------------------------------------------------------------------------
# Cross-tier isolation (lite valid duration is invalid for fast/standard)
# ---------------------------------------------------------------------------


class TestCrossTierIsolation:
    """Durations valid for one tier must be invalid for incompatible tiers."""

    @pytest.mark.parametrize("duration_s", [4, 5, 6])
    def test_lite_durations_are_invalid_for_fast(self, duration_s: int):
        with pytest.raises(VeoTierMismatch):
            validate("fast", duration_s)

    @pytest.mark.parametrize("duration_s", [4, 5, 6])
    def test_lite_durations_are_invalid_for_standard(self, duration_s: int):
        with pytest.raises(VeoTierMismatch):
            validate("standard", duration_s)

    def test_fast_duration_is_invalid_for_lite(self):
        with pytest.raises(VeoTierMismatch):
            validate("lite", 8)
