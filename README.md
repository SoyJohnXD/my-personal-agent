# My Personal Agent

Python personal assistant with CLI and Telegram gateways, Pydantic AI tools, and SQLite persistence.

## Environment

Keep these environment variable names unchanged:

- `AGENT_NAME` — assistant identity and SQLite database file name.
- `USER_NAME` — owner name used in the system prompt.
- `API_KEY` — OpenAI-compatible provider API key.
- `API_BASE_URL` — OpenAI-compatible provider base URL.
- `MODEL_NAME` — chat model name.
- `TELEGRAM_TOKEN` — required only when starting the Telegram gateway.

The CLI does not require `TELEGRAM_TOKEN`. Database files stay under `storage/db/{AGENT_NAME}.db`; the dashboard script keeps using that storage path.

## Local checks

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m compileall src
```
