from __future__ import annotations

import asyncio
import os
import uuid
from typing import List, Optional

from .models import FacebookMCPConfig, PostResult


class MCPClient:
    """
    Minimal MCP STDIO client wrapper.

    NOTE: This Phase-1 implementation provides a simulation mode (default) because
    a full MCP protocol client is out of scope here. For production, replace the
    _post_via_mcp stub with a real MCP client call.
    """

    def __init__(self, cfg: FacebookMCPConfig, fake_mode: Optional[bool] = None):
        self.cfg = cfg
        self.proc: Optional[asyncio.subprocess.Process] = None
        self.fake_mode = fake_mode if fake_mode is not None else bool(os.getenv("MCP_FAKE_MODE", "1") != "0")

    async def __aenter__(self):
        if not self.fake_mode:
            self.proc = await asyncio.create_subprocess_exec(
                self.cfg.command, *self.cfg.args, stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE
            )
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.proc:
            self.proc.terminate()
            try:
                await asyncio.wait_for(self.proc.wait(), timeout=5)
            except asyncio.TimeoutError:
                self.proc.kill()
        self.proc = None

    async def list_tools(self) -> List[str]:
        # In fake mode, we don't have tool discovery; return placeholder
        return ["post_to_facebook"]

    async def post_text(self, page_id: str, message: str) -> PostResult:
        if self.fake_mode:
            return PostResult(success=True, post_id=f"sim-{uuid.uuid4().hex}", page_id=page_id, error=None)

        # Placeholder for real MCP interaction
        tools = await self.list_tools()
        if "post_to_facebook" not in tools:
            raise RuntimeError(f"MCP tool 'post_to_facebook' not found. Available: {tools}")

        # Real implementation would marshal a JSON-RPC request to MCP server here.
        # For now, raise to signal incomplete integration if fake mode is off.
        raise RuntimeError("Real MCP STDIO integration not implemented in Phase-1. Enable fake mode or mock in tests.")

