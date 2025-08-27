# Archon production deployment on archon.v1su4.com (Coolify)

This document captures the working production configuration for your Archon deployment on Coolify at archon.v1su4.com, plus gotchas we encountered and best practices to follow.

Supported services and images (Docker Hub):
- gordov1su4/archon-server:v6.1
- gordov1su4/archon-mcp:v2.6
- gordov1su4/archon-agents:v2.1
- gordov1su4/archon-frontend:v2.6

Note: Tag numbers reflect the known-good images currently referenced by docker-compose.yaml in this repo. If you switch to using "latest", consider enabling webhook-triggered redeploys in Coolify.

## Prerequisites

- Supabase project created with the schema applied from migration/complete_setup.sql
- Supabase service_role key (not the anon key)
- OpenAI API key (or your chosen model provider configured in the UI later)
- Coolify app configured to deploy this repository using Docker Compose

## Compose configuration and routing

Use the docker-compose.yaml in the root of this repo as-is. It contains Traefik labels for https routing on archon.v1su4.com with these key points:

- Frontend served at the root path / on archon.v1su4.com
- API and Socket.IO routed via archon.v1su4.com/api and /socket.io
- MCP server routed via archon.v1su4.com/mcp with StripPrefix so requests reach the container at /

Important for MCP (FastMCP streamable-http):
- The client initiates with a POST to /mcp (JSON-RPC initialize), then the server upgrades to SSE internally.
- A direct GET to /mcp/sse will return 404 by design; this is expected with streamable-http. Don’t treat it as a failure.

The crucial Traefik StripPrefix config for MCP looks like this (already present in docker-compose.yaml):

- traefik.http.routers.archon-mcp.rule=Host(`archon.v1su4.com`) && (PathPrefix(`/mcp`) || Path(`/mcp/sse`))
- traefik.http.middlewares.archon-mcp-strip.stripprefix.prefixes=/mcp
- traefik.http.routers.archon-mcp.middlewares=archon-mcp-strip

## Environment variables in Coolify

Set the following at the application-level in Coolify (Environment → Variables):

Required:
- SUPABASE_URL=https://…your-project….supabase.co
- SUPABASE_SERVICE_KEY=…your service_role key… (not the anon key)
- OPENAI_API_KEY=…your key… (optional if you’ll set providers via the UI)

Frontend configuration:
- VITE_API_URL=https://archon.v1su4.com:8181
- ARCHON_MCP_PORT=443  (so the UI generates a https MCP URL)

Server service ports (already provided via compose):
- ARCHON_SERVER_PORT=8181
- ARCHON_MCP_PORT=8051
- ARCHON_AGENTS_PORT=8052

## Deploy steps in Coolify

1) Create or use an existing Docker Compose application and point it at this repository on the main branch.
2) Ensure the service ports 3737 (frontend), 8181 (server), 8051 (mcp), 8052 (agents) are exposed in Coolify as needed.
3) Set the environment variables above.
4) Deploy.

After deploy:
- Visit https://archon.v1su4.com and open Settings to configure your model providers.
- For MCP clients (Claude Code, Cursor, Windsurf, etc.), use the MCP URL shown on the MCP page in the UI (it resolves to your domain automatically). Example: https://archon.v1su4.com/mcp

## GitHub Actions (build and deploy)

This repo includes a workflow that builds and pushes all four images to Docker Hub when changes land on main:
- .github/workflows/deploy-coolify.yml
  - Builds: archon-server, archon-mcp, archon-agents, archon-frontend
  - Pushes to Docker Hub under gordov1su4/archon-<service>
  - Tags include latest on default branch, branch/PR refs, and commit SHA
  - Optionally triggers a Coolify webhook (set COOLIFY_WEBHOOK_URL) to redeploy

Two release strategies you can choose from:
- Pinned tags in docker-compose.yaml (recommended for stability). You bump tags when you want to roll forward.
- Floating "latest" tags in docker-compose.yaml plus an automatic webhook redeploy after each push to main.

## Known issues and best practices

- esbuild + Alpine: esbuild can panic in Alpine-based builds. We standardized on Node 20 and ensured libc compatibility in the frontend image. Our current frontend image builds are stable.
- FastMCP parameters: Older FastMCP versions rejected certain constructor args; the server code is aligned with the newer API and uses transport="streamable-http".
- MCP SSE endpoint: With streamable-http, a direct GET /mcp/sse returns 404. This is normal. The initialize POST returns a valid SSE session in response.
- Traefik path handling: Always strip the /mcp prefix so the MCP container receives / and /sse internally.
- Prefer pinned tags in production, and bump intentionally when promoting images you’ve validated.

If you need to override images or ports, adjust docker-compose.yaml and redeploy in Coolify.
