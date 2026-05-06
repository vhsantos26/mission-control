from src.pricing import cost_for_session


def test_sonnet_pricing_ballpark():
    cost = cost_for_session(
        model="claude-sonnet-4-6",
        input_tokens=1_000_000,
        output_tokens=500_000,
        cache_tokens=0,
    )
    # Sonnet: $3/M in, $15/M out -> $3 + $7.5 = $10.5
    assert 10.0 < cost < 11.0


def test_opus_pricing_ballpark():
    cost = cost_for_session(
        model="claude-opus-4-7",
        input_tokens=100_000,
        output_tokens=50_000,
        cache_tokens=0,
    )
    # Opus: $15/M in, $75/M out -> $1.5 + $3.75 = $5.25
    assert 5.0 < cost < 5.5


def test_max_plan_returns_zero():
    cost = cost_for_session(
        model="claude-sonnet-4-6",
        input_tokens=1_000_000,
        output_tokens=500_000,
        cache_tokens=0,
        plan="max20x",
    )
    assert cost == 0.0


def test_pro_plan_returns_zero():
    cost = cost_for_session(
        model="claude-sonnet-4-6",
        input_tokens=1_000_000,
        output_tokens=500_000,
        cache_tokens=0,
        plan="pro",
    )
    assert cost == 0.0


def test_unknown_model_returns_zero():
    cost = cost_for_session(
        model="unknown-model",
        input_tokens=100,
        output_tokens=50,
        cache_tokens=0,
    )
    assert cost == 0.0


def test_cache_read_is_cheap():
    cost = cost_for_session(
        model="claude-sonnet-4-6",
        input_tokens=0,
        output_tokens=0,
        cache_read_tokens=1_000_000,
    )
    # Sonnet cache read: $0.30/M
    assert 0.25 < cost < 0.35


def test_cache_create_is_more_than_input():
    create_cost = cost_for_session(
        model="claude-sonnet-4-6",
        input_tokens=0,
        output_tokens=0,
        cache_create_tokens=1_000_000,
    )
    input_cost = cost_for_session(
        model="claude-sonnet-4-6",
        input_tokens=1_000_000,
        output_tokens=0,
    )
    # Cache create is ~1.25× input
    assert create_cost > input_cost
    assert create_cost < input_cost * 1.5


def test_gpt4o_pricing_ballpark():
    cost = cost_for_session(
        model="gpt-4o",
        input_tokens=1_000_000,
        output_tokens=500_000,
    )
    # gpt-4o: $2.50/M in, $10/M out -> $2.50 + $5 = $7.50
    assert 7.0 < cost < 8.0


def test_codex_model_resolves_via_prefix():
    # The CLI version "gpt-5.3-codex-2026-01" should resolve to "gpt-5.3-codex"
    cost = cost_for_session(
        model="gpt-5.3-codex-2026-01",
        input_tokens=1_000_000,
        output_tokens=0,
    )
    assert cost > 0  # not the unknown-model zero


def test_openai_cached_input_is_half_price():
    # OpenAI bills cached input at 50% of input.
    fresh = cost_for_session(
        model="gpt-4o",
        input_tokens=1_000_000,
        output_tokens=0,
    )
    cached = cost_for_session(
        model="gpt-4o",
        input_tokens=0,
        output_tokens=0,
        cache_read_tokens=1_000_000,
    )
    assert abs(cached - fresh / 2) < 0.01


def test_openai_cache_create_is_zero_priced():
    # OpenAI does not bill cache create separately — cost should be 0.
    cost = cost_for_session(
        model="gpt-4o",
        input_tokens=0,
        output_tokens=0,
        cache_create_tokens=1_000_000,
    )
    assert cost == 0.0


def test_legacy_cache_tokens_arg_treated_as_cache_read():
    legacy = cost_for_session(
        model="claude-sonnet-4-6",
        input_tokens=0,
        output_tokens=0,
        cache_tokens=1_000_000,
    )
    explicit = cost_for_session(
        model="claude-sonnet-4-6",
        input_tokens=0,
        output_tokens=0,
        cache_read_tokens=1_000_000,
    )
    assert legacy == explicit
