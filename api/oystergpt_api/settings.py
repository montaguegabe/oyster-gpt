import os

# The prototypes pool shares one ANTHROPIC_API_KEY secret across its apps.
OYSTERGPT_ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
# Hard cap on Anthropic spend per UTC day, in dollars.
OYSTERGPT_DAILY_BUDGET_USD = os.environ.get("OYSTERGPT_DAILY_BUDGET_USD", "2.00")
# Worst-case cost of one message (about 40k input tokens with a web search, plus 1.5k output),
# reserved before each call so concurrent messages cannot overspend.
OYSTERGPT_REQUEST_RESERVE_USD = os.environ.get("OYSTERGPT_REQUEST_RESERVE_USD", "0.30")
