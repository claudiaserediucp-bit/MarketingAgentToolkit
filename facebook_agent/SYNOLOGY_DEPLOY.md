# Synology NAS Deployment Guide

## Prerequisites
- Synology NAS with Docker installed
- SSH access to the NAS
- OpenAI API key
- Facebook page long-lived access token and page ID

## 1. Upload/Clone Code to NAS

SSH into your Synology:
```bash
ssh -p 1313 your_user@your_nas_ip
```

Clone or upload the repository:
```bash
cd /volume1/docker
git clone https://github.com/claudiaserediucp-bit/MarketingAgentToolkit.git
cd MarketingAgentToolkit/facebook_agent
```

## 2. Create Environment File

Copy the template and fill in your credentials:
```bash
cp env.template .env
nano .env
```

Fill in:
- `OPENAI_API_KEY`: Your OpenAI API key
- `FACEBOOK_ACCESS_TOKEN`: Long-lived page access token from `facebook_tokens.json`
- `FACEBOOK_PAGE_ID`: Your Facebook page ID
- `MCP_FAKE_MODE`: Set to `0` for real posting

## 3. Create Logs Directory

```bash
mkdir -p /volume1/data/logs
```

## 4. Build and Run

Start both MCP server and agent:
```bash
docker-compose up --build
```

Or run in detached mode:
```bash
docker-compose up -d --build
```

## 5. Check Logs

View agent logs:
```bash
docker-compose logs -f fb-agent
```

View MCP server logs:
```bash
docker-compose logs -f facebook-mcp
```

Check posts log:
```bash
cat /volume1/data/logs/posts_log.csv
```

## 6. Stop Services

```bash
docker-compose down
```

## Scheduling with Cron

To run the agent periodically (e.g., every 30 minutes):

1. Create a script `/volume1/docker/MarketingAgentToolkit/facebook_agent/run_agent.sh`:
```bash
#!/bin/bash
cd /volume1/docker/MarketingAgentToolkit/facebook_agent
docker-compose run --rm fb-agent
```

2. Make it executable:
```bash
chmod +x run_agent.sh
```

3. Add to crontab:
```bash
crontab -e
```

Add line:
```
*/30 * * * * /volume1/docker/MarketingAgentToolkit/facebook_agent/run_agent.sh >> /volume1/data/logs/agent_cron.log 2>&1
```

## Testing with Forced Time

To test a specific slot time (e.g., morning slot at 09:05 Bucharest):
```bash
docker-compose run --rm fb-agent python -c "from datetime import datetime, timezone; from pathlib import Path; import asyncio; from facebook_agent.agent.agent_core import run_once; asyncio.run(run_once(Path('facebook_agent'), datetime(2026,1,2,7,5,tzinfo=timezone.utc)))"
```

## Troubleshooting

**MCP connection timeout:**
- Check if `facebook-mcp` container is running: `docker ps`
- View MCP logs: `docker-compose logs facebook-mcp`
- Ensure both containers are on the same network

**No posts generated:**
- Check if current time matches a scheduled slot in `config/clients/*.json`
- View agent logs for scheduling decisions
- Run with forced time (see above) to test a known slot

**Permission denied on logs:**
- Ensure `/volume1/data/logs` is writable: `chmod 777 /volume1/data/logs`

## Architecture

```
┌─────────────────┐
│   fb-agent      │
│  (marketing)    │
│                 │
│  • OpenAI LLM   │
│  • Scheduler    │
│  • Logger       │
└────────┬────────┘
         │ docker exec -i
         │ (stdio JSON-RPC)
         ▼
┌─────────────────┐
│ facebook-mcp    │
│  (MCP server)   │
│                 │
│  • Graph API    │
│  • Tools        │
└─────────────────┘
```

Both containers run on the same Docker network. The agent calls MCP via `docker exec -i` over stdio (no SSH, no network ports).

