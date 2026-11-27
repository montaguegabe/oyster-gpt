from decimal import Decimal
from types import SimpleNamespace

from oystergpt_api.oystergpt.oyster import MODEL, SILENCE, oysterize, usage_cost


def make_usage(
    input_tokens=0, output_tokens=0, searches=0, cache_write=0, cache_read=0
):
    return SimpleNamespace(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_creation_input_tokens=cache_write,
        cache_read_input_tokens=cache_read,
        server_tool_use=SimpleNamespace(web_search_requests=searches),
    )


def test_oysterize_keeps_only_blubs():
    assert oysterize("Sure! Here's a poem about the sea.") == SILENCE
    assert oysterize("...") == SILENCE
    assert oysterize("Blub blub.") == "blub blub"
    assert oysterize("*blub") == "*blub*"
    assert oysterize("I am an oyster, bluuuub!") == "bluuuub"


def test_usage_cost_prices_opus_tokens_and_searches():
    # The probe that sized the guard: 20,031 input, 306 output, one search, about $0.096.
    cost = usage_cost(
        MODEL, make_usage(input_tokens=20_031, output_tokens=306, searches=1)
    )
    assert cost == Decimal("0.080124") + Decimal("0.00612") + Decimal("0.01")


def test_usage_cost_prices_unknown_fallback_models_at_the_top_tier():
    assert usage_cost("claude-unknown", make_usage(output_tokens=1_000_000)) == Decimal(
        50
    )
