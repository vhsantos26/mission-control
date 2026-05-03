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


def test_cache_tokens_priced_lower():
    no_cache = cost_for_session(
        model="claude-sonnet-4-6",
        input_tokens=1_000_000,
        output_tokens=0,
        cache_tokens=0,
    )
    with_cache = cost_for_session(
        model="claude-sonnet-4-6",
        input_tokens=0,
        output_tokens=0,
        cache_tokens=1_000_000,
    )
    # Cache reads are about 10x cheaper than fresh input
    assert with_cache < no_cache / 5
