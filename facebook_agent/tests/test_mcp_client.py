import asyncio

import pytest

from facebook_agent.agent.mcp_client import MCPClient
from facebook_agent.agent.models import FacebookMCPConfig


@pytest.mark.asyncio
async def test_mcp_client_fake_mode():
    cfg = FacebookMCPConfig(command="echo", args=["ok"])
    async with MCPClient(cfg, fake_mode=True) as mcp:
        tools = await mcp.list_tools()
        assert "post_to_facebook" in tools
        res = await mcp.post_text(page_id="p1", message="hello")
        assert res.success
        assert res.post_id.startswith("sim-")

