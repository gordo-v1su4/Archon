# Conversation Log — Archon MCP Deployment and Frontend Updates

Date: 2025-08-28
Repo: C:\Users\Gordo\Documents\Github\Archon
Shell: Windows pwsh 7.5.2

Summary
- Built and pushed images:
  - gordov1su4/archon-frontend:v7.2 (UI shows correct MCP configs + stdio mcp-proxy helper)
  - gordov1su4/archon-server:v7.0
  - gordov1su4/archon-mcp:v7.1 (MCP mounted at /mcp)
  - gordov1su4/archon-agents:v7.0
- docker-compose.yaml (root) is the source of truth:
  - name: archon
  - archon-frontend: v7.2
  - archon-server: v7.0
  - archon-mcp: v7.1
  - archon-agents: v7.0
  - Traefik preserves /mcp (no StripPrefix), priority=1000 on MCP router, loadbalancer.port=8051
- MCP server code (python/src/mcp_server/mcp_server.py):
  - streamable_http_path set to "/mcp"
  - startup log shows URL http://0.0.0.0:8051/mcp
- Claude Code config:
  - Uses HTTP transport at https://archon.v1su4.com/mcp
  - .claude.json updated to type: "http" (SSE GET health check returns 400; HTTP POST works)
- Old CI removed: deleted .github/workflows (legacy and incorrect)

Endpoint checks (live)
- Frontend / => 200
- Server /health => 200
- Socket.IO handshake => 200
- MCP POST /mcp initialize => 200 OK (text/event-stream)
  - Mcp-Session-Id present
  - GET /mcp returns 400/406 by design

Claude Code — add Archon MCP (works on any computer)
- Command:
  claude mcp add --transport http archon https://archon.v1su4.com/mcp
- Minimal JSON format:
  { "name": "archon", "transport": "http", "url": "https://archon.v1su4.com/mcp" }

Stdio-only IDEs (e.g., Cline, Kiro)
- Use a local stdio bridge:
  mcp-proxy --stdio --target-url https://archon.v1su4.com/mcp --target-headers "Content-Type: application/json"
- The frontend UI now displays this helper under the MCP dashboard for those IDEs.

Coolify / Traefik notes
- Use .yaml (Coolify requirement)
- Do not StripPrefix for /mcp; preserve path to the container
- MCP router priority set high so it wins over frontend catch-all
- Health checks for MCP can be a POST JSON-RPC initialize (optional; image would need curl)

Compose references (final)
- archon-frontend: gordov1su4/archon-frontend:v7.2
- archon-server: gordov1su4/archon-server:v7.0
- archon-mcp: gordov1su4/archon-mcp:v7.1
- archon-agents: gordov1su4/archon-agents:v7.0

Build/push commands used
- MCP (v7.1):
  docker build -f python/Dockerfile.mcp -t gordov1su4/archon-mcp:v7.1 python
  docker push gordov1su4/archon-mcp:v7.1
- Frontend (v7.2):
  docker build -f archon-ui-main/Dockerfile -t gordov1su4/archon-frontend:v7.2 archon-ui-main
  docker push gordov1su4/archon-frontend:v7.2

Frontend changes
- File: archon-ui-main/src/pages/MCPPage.tsx
  - Claude Code block uses transport: "http" and resolves URL to /mcp
  - Added explicit mcp-proxy stdio instructions for Cline/Kiro

Git commits (local)
- ci: remove obsolete GitHub Actions workflows; docker-compose.yaml at repo root is source of truth for deployment
- deploy: bump all service images to v7.0 and preserve /mcp path in Traefik labels (no StripPrefix)
- deploy(ui): pin archon-frontend to v7.1 after TS import fix (compose is source of truth)
- ui(mcp): add stdio mcp-proxy instructions for Cline/Kiro; bump frontend to v7.2 and update compose

Security (future optional)
- Add Authorization: Bearer {{MCP_TOKEN}} to Claude headers and enforce on server
- Keep secrets out of logs, inject via env vars

Next actions (optional)
- Push these commits to your fork (not upstream) — provide remote and branch
- Add a simple healthcheck to MCP image if desired
- Add a short README section for MCP quickstart across IDEs

Resuming on another machine
- Install/launch Claude Code
- Run: claude mcp add --transport http archon https://archon.v1su4.com/mcp
- For stdio-only IDEs, run the mcp-proxy command above
- That’s it — no manual file copying required.

