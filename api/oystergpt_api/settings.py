import os

# OysterGPT keeps its own key so it never collides with another app's ANTHROPIC_API_KEY on a shared pool.
OYSTERGPT_ANTHROPIC_API_KEY = os.environ.get("OYSTERGPT_ANTHROPIC_API_KEY", "")
# Hard cap on Anthropic spend per UTC day, in dollars.
OYSTERGPT_DAILY_BUDGET_USD = os.environ.get("OYSTERGPT_DAILY_BUDGET_USD", "2.00")
# Worst-case cost of one message (about 40k input tokens with a web search, plus 1.5k output),
# reserved before each call so concurrent messages cannot overspend.
OYSTERGPT_REQUEST_RESERVE_USD = os.environ.get("OYSTERGPT_REQUEST_RESERVE_USD", "0.30")
