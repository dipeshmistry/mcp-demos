# MCP Demos

A collection of Model Context Protocol (MCP) proof-of-concept clients and servers,
built while learning and experimenting with MCP, stdio transports, JWT-secured
tool calls, and LLM-driven tool selection.

## Structure

- `clients/mcp-clients` - general-purpose MCP client experiments (chat-style client, multi-tool client).
- `clients/test_client` - MCP client variants including JWT-authenticated calls and chat-history-aware calls.
- `servers/terminal_server` - a dockerized MCP server exposing terminal/shell-style tools.
- `servers/test_server` - a variant of the terminal server with JWT auth and unit tests.
- `servers/claud_config.txt` - example Claude Desktop MCP server configuration.
- `simple-client-server` - a minimal end-to-end MCP client/server pair (LLM picks a tool, e.g. a BMI calculator, from a natural-language query).
- `calculator-server` - a small MCP server exposing calculator tools, with a dev runner script.
- `workspace-notes` - scratch notes captured while testing MCP client/server behavior.

## Running

Each subproject uses [`uv`](https://docs.astral.sh/uv/) or `pip` with its own
`pyproject.toml` / `requirements.txt`. Typical flow:

```bash
cd <subproject>
uv sync            # or: pip install -r requirements.txt
cp .env.example .env   # if present - set OPENAI_API_KEY / secrets yourself
uv run main.py
```

No `.env` files or API keys are committed - set `OPENAI_API_KEY` (and any other
secret) in your own environment before running.
