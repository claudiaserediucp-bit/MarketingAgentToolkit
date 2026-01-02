# AI Social Media Marketing Agent (Phase 1)

One-shot cron-triggered Docker job that generates Facebook posts via OpenAI and posts through a Facebook MCP server over STDIO. Phase 1 keeps a single agent class (`SocialMediaAgent`) and JSON-only configs.

## Structure
```
facebook_agent/
  agent/        # code
  config/       # JSON configs
  tests/        # pytest suite (mocked LLM + MCP)
  Dockerfile
  requirements.txt
```

## Configs (JSON only)
- `config/global.json`: timezone, LLM, scheduler, MCP command, CSV logging path.
- `config/agents.json`: personas by `agent_id`.
- `config/clients/*.json`: client definitions (slots, campaigns, guardrails, platforms). Example provided in `example_client.json`.

## Running locally
```bash
cd facebook_agent
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=your_key
python -m facebook_agent.agent.main
```

## Running tests
```bash
cd facebook_agent
pytest
```
Tests are network-free: LLM and MCP are mocked.

## Docker build & run
```bash
cd facebook_agent
docker build -t fb-agent .
docker run --rm \
  -e OPENAI_API_KEY=your_key \
  -v $(pwd)/data/logs:/data/logs \
  fb-agent
```

## Cron example (Synology)
Schedule every 30 minutes:
```
*/30 * * * * docker run --rm -e OPENAI_API_KEY=$OPENAI_API_KEY -v /volume1/data/logs:/data/logs fb-agent
```

## Notes
- MCP command/args are read from `config/global.json` (mounted under `/app/facebook_agent/config` in the image).
- Logging appends to CSV (`/data/logs/posts_log.csv`).
- Instagram config is accepted but ignored in Phase 1.
- MCP client ships with a `fake` mode by default (`MCP_FAKE_MODE=1`). Set `MCP_FAKE_MODE=0` to attempt real MCP STDIO integration once available.

