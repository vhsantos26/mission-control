"""Cost calculation per Anthropic API pricing (USD per 1M tokens).

Reference: https://www.anthropic.com/pricing (Jan 2026 snapshot).
Plan-based subscriptions (Pro, Max, Max-20x) return zero cost — usage is flat.
"""

PRICING: dict[str, dict[str, float]] = {
    "claude-opus-4-7": {"input": 15.00, "output": 75.00, "cache_read": 1.50},
    "claude-sonnet-4-6": {"input": 3.00, "output": 15.00, "cache_read": 0.30},
    "claude-haiku-4-5": {"input": 0.80, "output": 4.00, "cache_read": 0.08},
    # Older versions kept for backfilling historical sessions
    "claude-opus-4-6": {"input": 15.00, "output": 75.00, "cache_read": 1.50},
    "claude-sonnet-4-5": {"input": 3.00, "output": 15.00, "cache_read": 0.30},
}

FLAT_PLANS = {"pro", "max", "max20x"}


def cost_for_session(
    model: str,
    input_tokens: int,
    output_tokens: int,
    cache_tokens: int,
    plan: str = "api",
) -> float:
    """Return cost in USD for a session's token usage.

    Returns 0.0 for flat-rate plans or unknown models.
    """
    if plan in FLAT_PLANS:
        return 0.0

    p = PRICING.get(model)
    if not p:
        return 0.0

    cost = (
        (input_tokens / 1_000_000) * p["input"]
        + (output_tokens / 1_000_000) * p["output"]
        + (cache_tokens / 1_000_000) * p.get("cache_read", 0)
    )
    return round(cost, 4)
