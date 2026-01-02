from __future__ import annotations

import asyncio
import os
import uuid
from typing import List, Optional

import json
from json import JSONDecodeError
from typing import List, Optional

from .models import FacebookMCPConfig, PostResult


class MCPClient:
    """
    Minimal MCP STDIO client wrapper.

    NOTE: This Phase-1 implementation provides a simulation mode (default). When
    MCP_FAKE_MODE=0 it will invoke the remote MCP server (Synology) over STDIO
    using JSON-RPC (FastMCP). Tool name expected: post_to_facebook(message).
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

        # Real MCP JSON-RPC call over STDIO
        if not self.proc or not self.proc.stdin or not self.proc.stdout:
            raise RuntimeError("MCP process not started")

        req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "post_to_facebook",
            "params": {"message": message},
        }
        payload = (json.dumps(req) + "\n").encode("utf-8")
        self.proc.stdin.write(payload)
        await self.proc.stdin.drain()

        try:
            line = await asyncio.wait_for(self.proc.stdout.readline(), timeout=30)
        except asyncio.TimeoutError:
            return PostResult(success=False, post_id=None, page_id=page_id, error="Timeout waiting for MCP response")

        try:
            resp = json.loads(line.decode("utf-8"))
        except JSONDecodeError:
            return PostResult(success=False, post_id=None, page_id=page_id, error=f"Invalid MCP response: {line!r}")

        if "error" in resp:
            return PostResult(success=False, post_id=None, page_id=page_id, error=str(resp["error"]))

        result = resp.get("result", {})
        post_id = result.get("id") or result.get("post_id") or result.get("result") or result.get("data")
        return PostResult(success=True, post_id=str(post_id) if post_id is not None else None, page_id=page_id, error=None)

