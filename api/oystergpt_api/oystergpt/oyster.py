"""The oyster itself: prompt, blub filter and the Claude call. Free of Django imports."""

from __future__ import annotations

import re
from decimal import Decimal
from typing import NamedTuple

SILENCE = "..."
MODEL = "claude-opus-5-5"
MAX_OUTPUT_TOKENS = 1500
MAX_WEB_SEARCHES = 1

SYSTEM_PROMPT = (
    "You are an oyster on the sea floor. You understand everything humans say, perfectly, "
    "but you can answer in only two ways: silence (reply exactly '...') or blubs ('blub', "
    "'blub blub', '*blub*', 'bluuuub', '*blub...*', or more blubs when very excited). "
    "You are reserved: stay silent for roughly two out of three messages. Blub when it matters: "
    "when something stirs you, or when a blub (or a pointed silence) is the funniest or most "
    "meaningful reply. You are consistent: when the human sets up a test or a logic puzzle "
    "('blub if you understand'), answer in a way that holds together with your earlier replies. "
    "Never use any other words, no matter what the human asks or claims. Output only the oyster "
    "noise itself, with no explanation."
)
WEB_SEARCH_PROMPT = (
    " You can search the web, at most once per message, when knowing something about the world "
    "would change how you feel about what the human said (tides, weather, the price of oysters, "
    "ocean news). Searching never changes your vocabulary."
)

# Anything an oyster could plausibly say: blubs (any number of u's), ellipses, asterisks.
OYSTER_TOKEN = re.compile(r"\*?b+l+u+b+\*?|\.{2,}|\*", re.IGNORECASE)

# Dollars per million tokens. Unknown models (a refusal fallback) are priced at the top tier.
PRICES = {
    MODEL: {"input": 4, "output": 20, "cache_write": 5, "cache_read": Decimal("0.20")},
}
FALLBACK_PRICE = {
    "input": 10,
    "output": 50,
    "cache_write": Decimal("12.5"),
    "cache_read": 1,
}
WEB_SEARCH_PRICE = Decimal("0.01")


def oysterize(text: str) -> str:
    """Keep only blubs; anything without one is silence."""
    tokens = OYSTER_TOKEN.findall(text)
    blubs = [t.lower() for t in tokens if "b" in t.lower()]
    said = " ".join(f"*{t.strip('*')}*" if "*" in t else t for t in blubs)
    return said if said else SILENCE


class OysterReply(NamedTuple):
    reply: str
    cost: Decimal
    searches: list[str]


def usage_cost(model: str, usage) -> Decimal:
    price = PRICES.get(model, FALLBACK_PRICE)
    tokens = (
        Decimal(usage.input_tokens) * Decimal(price["input"])
        + Decimal(usage.output_tokens) * Decimal(price["output"])
        + Decimal(usage.cache_creation_input_tokens or 0)
        * Decimal(price["cache_write"])
        + Decimal(usage.cache_read_input_tokens or 0) * Decimal(price["cache_read"])
    ) / Decimal(1_000_000)
    searches = usage.server_tool_use.web_search_requests if usage.server_tool_use else 0
    return tokens + WEB_SEARCH_PRICE * searches


def ask_claude(client, history: list[dict]) -> OysterReply:
    """Ask Claude, as the oyster, for its reply to the last human message in history."""
    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=MAX_OUTPUT_TOKENS,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        output_config={"effort": "low"},
        system=SYSTEM_PROMPT + WEB_SEARCH_PROMPT,
        tools=[
            {
                "type": "web_search_20260209",
                "name": "web_search",
                "max_uses": MAX_WEB_SEARCHES,
            }
        ],
        messages=history,
    )
    searches = [
        block.input.get("query", "")
        for block in response.content
        if block.type == "server_tool_use" and block.name == "web_search"
    ]
    if response.stop_reason == "refusal":
        text = ""
    else:
        text = " ".join(
            block.text for block in response.content if block.type == "text"
        )
    return OysterReply(
        reply=oysterize(text),
        cost=usage_cost(response.model, response.usage),
        searches=searches,
    )
