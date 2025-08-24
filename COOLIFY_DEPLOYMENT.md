# Archon Coolify Deployment Guide

## Prerequisites

### 1. Setup Supabase Database

Before deploying to Coolify, you need to create the database schema in your Supabase project:

1. Go to your Supabase Dashboard: https://supabase.com/dashboard
2. Select your project (https://caqboqcartvhzvdjitry.supabase.co)
3. Navigate to **SQL Editor** in the left sidebar
4. Click **New Query**
5. Copy and paste the entire contents of `migration/complete_setup.sql`
6. Click **Run** to execute the SQL

This will create all necessary tables including:
- `archon_settings` - Configuration and API keys
- `archon_sources` - Knowledge base sources
- `archon_crawled_pages` - Document chunks
- `archon_code_examples` - Extracted code
- `archon_projects` - Project management
- And more...

### 2. Get Your Supabase Service Key

⚠️ **IMPORTANT**: You need the **service_role** key, NOT the anon key!

1. In Supabase Dashboard, go to **Settings** → **API**
2. Find the **service_role** key (has full database access)
3. Copy this key for the `SUPABASE_SERVICE_KEY` environment variable

## Coolify Deployment

### 1. Docker Compose Configuration

Use this `docker-compose.yaml`:

```yaml
services:
  archon-server:
    image: gordov1su4/archon-server:v3.0
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LOG_LEVEL=INFO
      - ARCHON_SERVER_PORT=8181
      - ARCHON_MCP_PORT=8051
      - ARCHON_AGENTS_PORT=8052
  
  archon-mcp:
    image: gordov1su4/archon-mcp:v2.0
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
      - API_SERVICE_URL=http://archon-server:8181
      - AGENTS_SERVICE_URL=http://archon-agents:8052
      - ARCHON_MCP_PORT=8051
    depends_on:
      - archon-server
      - archon-agents
  
  archon-agents:
    image: gordov1su4/archon-agents:v2.0
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LOG_LEVEL=INFO
      - ARCHON_AGENTS_PORT=8052
  
  archon-frontend:
    image: gordov1su4/archon-frontend:v2.0
    environment:
      - VITE_API_URL=${VITE_API_URL:-https://archon.v1su4.com:8181}
      - VITE_ARCHON_SERVER_PORT=8181
      - ARCHON_SERVER_PORT=8181
      - HOST=0.0.0.0
    depends_on:
      - archon-server
```

### 2. Environment Variables in Coolify

Set these in your Coolify environment:

```env
# Database Configuration
SUPABASE_URL=https://caqboqcartvhzvdjitry.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key_here  # NOT the anon key!

# API Keys
OPENAI_API_KEY=your_openai_api_key_here

# Frontend Configuration (update with your domain)
VITE_API_URL=https://archon.v1su4.com:8181
```

### 3. Port Configuration

Make sure these ports are exposed in Coolify:
- **8181** - Backend API Server
- **8051** - MCP Server
- **8052** - Agents Server  
- **3737** - Frontend UI

### 4. Deploy

1. Create a new service in Coolify
2. Choose "Docker Compose" deployment
3. Paste the docker-compose.yaml
4. Set the environment variables
5. Deploy!

## Troubleshooting

### "Could not find table" Error
- Make sure you ran the SQL migration in Supabase first
- Verify the table exists in Supabase Table Editor

### "Permission denied" or "ANON_KEY_DETECTED" Error
- You're using the wrong Supabase key
- Use the `service_role` key, not the `anon` key

### Docker Build Errors
- The images are pre-built on Docker Hub
- No building required in Coolify
- Just pulls and runs

## Docker Images

All images are public on Docker Hub:
- `gordov1su4/archon-server:v3.0` - Fixed Python error
- `gordov1su4/archon-agents:v2.0`
- `gordov1su4/archon-mcp:v2.0`
- `gordov1su4/archon-frontend:v2.0`
