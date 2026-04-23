"""D033 tier × duration validation for Veo video generation.

This module owns:
- The exception hierarchy for all Veo tool errors
- The D033 validation matrix (VALID_COMBINATIONS)
- The validate() guard called BEFORE any API submission

Design decision: validation failures raise typed exceptions so the
video-generator agent can route recovery (Ken-Burns, wait, abort)
without parsing error strings. This module never catches and re-raises
exceptions generically — specific types propagate to the caller.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


class VeoError(Exception):
    """Base exception for all Veo tool errors.

    Callers should catch specific sub-types to choose their recovery path:
    - VeoQuotaExhausted → Ken-Burns fallback (agent decision, NOT tool)
    - VeoTierMismatch   → Fix input params and retry
    - VeoTimeout        → Retry with backoff or abort
    - VeoAPIError       → Inspect status_code; may be retryable
    """


class VeoQuotaExhausted(VeoError):
    """Raised after exhausting all retry attempts on 429 RESOURCE_EXHAUSTED.

    The AGENT (not this tool) is responsible for Ken-Burns fallback when
    this fires. The tool's job ends here — it raises and gets out of the way.

    Attributes:
        retry_after_s: Suggested wait time from the API, or None if unknown.
    """

    def __init__(self, retry_after_s: int | None = None) -> None:
        self.retry_after_s = retry_after_s
        hint = f"Retry after {retry_after_s}s." if retry_after_s else "Retry time unknown."
        super().__init__(
            f"Veo quota exhausted after all retry attempts. {hint} "
            "Agent should route to Ken-Burns fallback or wait and retry."
        )


class VeoTierMismatch(VeoError):
    """Raised when (tier, duration_s) violates the D033 validation matrix.

    This fires in two situations:
    1. Pre-flight: validate() rejects the pair before sending to API
    2. Post-submission: API returns 400 INVALID_ARGUMENT with tier/duration language

    Attributes:
        tier:     The tier that was requested (e.g. "lite")
        duration: The duration_s that was requested
        expected: The set of durations valid for this tier per D033
    """

    def __init__(self, tier: str, duration: int, expected: set[int]) -> None:
        self.tier = tier
        self.duration = duration
        self.expected = expected
        super().__init__(
            f"D033 violation: tier='{tier}' does not allow duration_s={duration}. "
            f"Allowed durations for '{tier}': {sorted(expected)}. "
            "See VALID_COMBINATIONS in validation.py (decision D033)."
        )


class VeoTimeout(VeoError):
    """Raised when operation polling exceeds the configured maximum wait.

    Attributes:
        elapsed_s: How many seconds were spent polling before giving up.
    """

    def __init__(self, elapsed_s: int) -> None:
        self.elapsed_s = elapsed_s
        super().__init__(
            f"Veo operation timed out after {elapsed_s}s of polling. "
            "The generation job may still be running on Google's side."
        )


class VeoAPIError(VeoError):
    """Raised for API errors not covered by the more specific exception types.

    Attributes:
        status_code: HTTP status code (0 if unknown / SDK-level error)
        message:     Raw error message from the API or SDK
    """

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(f"Veo API error {status_code}: {message}")


# ---------------------------------------------------------------------------
# D033 validation matrix
# ---------------------------------------------------------------------------

# Tier → set of allowed duration_s values (per decision D033)
#
# Deviations are rejected BEFORE submitting to the API, which avoids
# burning quota on guaranteed-to-fail requests.
#
# "lite"     → 4, 5, or 6 seconds  (short-form / social content)
# "fast"     → 8 seconds only      (speed-optimised render)
# "standard" → 8 seconds only      (higher-quality render, same timeline)
VALID_COMBINATIONS: dict[str, set[int]] = {
    "lite": {4, 5, 6},
    "fast": {8},
    "standard": {8},
}

KNOWN_TIERS: frozenset[str] = frozenset(VALID_COMBINATIONS)


def validate(tier: str, duration_s: int) -> None:
    """Validate a (tier, duration_s) pair against the D033 rules.

    Called BEFORE submitting to the Veo API so no quota is burned on
    invalid requests.

    Args:
        tier:       One of "lite", "fast", "standard".
        duration_s: Requested video duration in seconds.

    Raises:
        ValueError:      If ``tier`` is not a recognised tier name.
        VeoTierMismatch: If the (tier, duration_s) pair violates D033.

    Examples:
        >>> validate("lite", 5)      # OK — no exception
        >>> validate("fast", 8)      # OK — no exception
        >>> validate("lite", 8)      # Raises VeoTierMismatch
        >>> validate("unknown", 5)   # Raises ValueError
    """
    if tier not in KNOWN_TIERS:
        raise ValueError(
            f"Unknown tier '{tier}'. Known tiers: {sorted(KNOWN_TIERS)}. "
            "Check VALID_COMBINATIONS in validation.py."
        )
    allowed = VALID_COMBINATIONS[tier]
    if duration_s not in allowed:
        raise VeoTierMismatch(tier=tier, duration=duration_s, expected=allowed)
