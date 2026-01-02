# MCP Registry

Use this folder to register MCP servers that agents can consume.

Current entry:

- `facebook_mcp_nas`: runs the Facebook MCP server over SSH on port `1313`:
  - Command: `ssh`
  - Args: `-p 1313 adiciok@ds2018 "cd /volume1/docker/facebook-mcp/facebook-mcp-server && docker-compose run --rm facebook-mcp"`

Point your MCP client config at `registry/mcp_servers.json`.

