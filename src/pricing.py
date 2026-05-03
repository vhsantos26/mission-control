"""Cost calculation per Anthropic API pricing (USD per 1M tokens).

Reference: https://www.anthropic.com/pricing (Jan 2026 snapshot).

Cache create costs more than fresh input (1.25× for 5-min ephemeral); cache
reads are ~10× cheaper than input. Lumping them together (as v0.3 did) hides
the real composition. v0.4 prices each separately.

Plan-based subscriptions (Pro, Max, Max-20x) return zero cost — usage is flat.
"""

# Per-1M tokens (USD)
#   input:        fresh input
#   output:       generated tokens
#   cache_create: 5-min ephemeral cache write (≈ 1.25× input)
#   cache_read:   cache hit (≈ 0.1× input)
PRICING: dict[str, dict[str, float]] = {
    "claude-opus-4-7": {
        "input": 15.00, "output": 75.00,
        "cache_create": 18.75, "cache_read": 1.50,
    },
    "claude-sonnet-4-6": {
        "input": 3.00, "output": 15.00,
        "cache_create": 3.75, "cache_read": 0.30,
    },
    "claude-haiku-4-5": {
        "input": 0.80, "output": 4.00,
        "cache_create": 1.00, "cache_read": 0.08,
    },
    # Older versions kept for backfilling historical sessions
    "claude-opus-4-6": {
        "input": 15.00, "output": 75.00,
        "cache_create": 18.75, "cache_read": 1.50,
    },
    "claude-sonnet-4-5": {
        "input": 3.00, "output": 15.00,
        "cache_create": 3.75, "cache_read": 0.30,
    },
}

FLAT_PLANS = {"pro", "max", "max20x"}


def cost_for_session(
    model: str,
    input_tokens: int,
    output_tokens: int,
    cache_read_tokens: int = 0,
    cache_create_tokens: int = 0,
    plan: str = "api",
    # Back-compat: callers passing single 'cache_tokens' get treated as all-read
    cache_tokens: int | None = None,
) -> float:
    """Return cost in USD for a session's token usage.

    Returns 0.0 for flat-rate plans or unknown models. If only the legacy
    ``cache_tokens`` arg is given, it's treated as cache_read (conservative
    underestimate vs. cache_create).
    """
    if plan in FLAT_PLANS:
        return 0.0

    p = PRICING.get(model)
    if not p:
        return 0.0

    if cache_tokens is not None and cache_read_tokens == 0 and cache_create_tokens == 0:
        cache_read_tokens = cache_tokens

    cost = (
        (input_tokens / 1_000_000) * p["input"]
        + (output_tokens / 1_000_000) * p["output"]
        + (cache_read_tokens / 1_000_000) * p.get("cache_read", 0)
        + (cache_create_tokens / 1_000_000) * p.get("cache_create", 0)
    )
    return round(cost, 4)
