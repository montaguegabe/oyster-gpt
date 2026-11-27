# OysterGPT API

The deployable OysterGPT backend: an Openbase API Core app package (`oystergpt_api`), mounted at `/api/oystergpt/`.

- `GET /api/oystergpt/` serves the chat page.
- `POST /api/oystergpt/chat/` asks Claude Opus 5.5, with web search, for the oyster's reply. It is public, so it is throttled (30 messages per hour per IP), and every message reserves its worst-case cost against a daily budget before calling the API (`OYSTERGPT_DAILY_BUDGET_USD`, default $2 per UTC day). Once the budget is spent, the oyster sleeps until tomorrow.
- Needs the secret `OYSTERGPT_ANTHROPIC_API_KEY`.

Tests run against api-core: `pytest -c <api-core>/pyproject.toml oystergpt_api/oystergpt/tests`.
