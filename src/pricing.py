"""Cost calculation per provider pricing (USD per 1M tokens).

Anthropic reference: https://www.anthropic.com/pricing (Jan 2026 snapshot).
OpenAI reference: https://openai.com/api/pricing (Jan 2026 snapshot).

Anthropic distinguishes ``cache_create`` (~1.25× input, 5-min ephemeral) from
``cache_read`` (~0.1× input). The 5× spread between them means lumping is
materially wrong — keep both separated everywhere.

OpenAI does not bill cache create separately: cached input is just charged at
half-price (50% discount). For OpenAI rows, ``cache_create`` stays at 0 in the
DB, and ``cache_read`` price is set to half of input.

Plan-based Anthropic subscriptions (Pro, Max, Max-20x) return zero cost —
usage is flat. There is no equivalent flat plan flag for OpenAI yet.

``gpt-5.3-codex`` does not have a public price sheet. We mirror ``gpt-5``
estimates; adjust this row when OpenAI publishes official numbers.
"""

# Per-1M tokens (USD)
#   input:        fresh input
#   output:       generated tokens
#   cache_create: ephemeral cache write (Anthropic only)
#   cache_read:   cache hit
PRICING: dict[str, dict[str, float]] = {
    # --- Anthropic ---
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
    "claude-opus-4-6": {
        "input": 15.00, "output": 75.00,
        "cache_create": 18.75, "cache_read": 1.50,
    },
    "claude-sonnet-4-5": {
        "input": 3.00, "output": 15.00,
        "cache_create": 3.75, "cache_read": 0.30,
    },
    # --- OpenAI ---
    # cache_create is unused for OpenAI; cache_read is input * 0.5.
    # OpenAI has not published official prices for gpt-5.x-codex variants —
    # these are estimates. Adjust when official numbers ship. Order matters:
    # _resolve_pricing uses longest-prefix match, so the more specific
    # ``-codex-mini`` row must be present alongside the family root.
    "gpt-5.3-codex": {
        "input": 5.00, "output": 20.00,
        "cache_create": 0.00, "cache_read": 2.50,
    },
    "gpt-5.1-codex-mini": {
        "input": 0.15, "output": 0.60,
        "cache_create": 0.00, "cache_read": 0.075,
    },
    "gpt-5-codex": {
        "input": 5.00, "output": 20.00,
        "cache_create": 0.00, "cache_read": 2.50,
    },
    "gpt-5": {
        "input": 5.00, "output": 20.00,
        "cache_create": 0.00, "cache_read": 2.50,
    },
    "gpt-4o": {
        "input": 2.50, "output": 10.00,
        "cache_create": 0.00, "cache_read": 1.25,
    },
    "gpt-4o-mini": {
        "input": 0.15, "output": 0.60,
        "cache_create": 0.00, "cache_read": 0.075,
    },
    "o1": {
        "input": 15.00, "output": 60.00,
        "cache_create": 0.00, "cache_read": 7.50,
    },
    "o1-mini": {
        "input": 1.10, "output": 4.40,
        "cache_create": 0.00, "cache_read": 0.55,
    },
    "o3-mini": {
        "input": 1.10, "output": 4.40,
        "cache_create": 0.00, "cache_read": 0.55,
    },
}


def _resolve_pricing(model: str) -> dict[str, float] | None:
    """Resolve a model id to its pricing row.

    Tries exact match first, then prefix-match against known model families
    (``gpt-5.3-codex`` → ``gpt-5``, ``claude-opus-4-7-20251225`` → ``claude-opus-4-7``).
    Returns None for unknown models so callers can charge $0 instead of guessing.
    """
    if model in PRICING:
        return PRICING[model]
    # Longest prefix wins so ``gpt-5.3-codex`` doesn't accidentally match ``gpt-5``
    # before ``gpt-5.3-codex`` in the iteration.
    candidates = [k for k in PRICING if model.startswith(k)]
    if not candidates:
        return None
    return PRICING[max(candidates, key=len)]

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

    p = _resolve_pricing(model)
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
