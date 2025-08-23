# Archon Coolify Deployment Guide

This guide will help you deploy Archon on Coolify with a self-hosted PostgreSQL database.

## Prerequisites

- Coolify instance running
- PostgreSQL database (can be self-hosted or managed)
- Docker and Docker Compose access

## Step 1: Database Setup

### Option A: Use Your Existing Supabase Database

If you want to use your existing Supabase setup with the environment variables you provided:

1. **Database Migration**: Run the migration script in your Supabase SQL Editor:
   ```sql
   -- Copy and paste the contents of migration/complete_setup.sql
   -- into your Supabase SQL Editor and execute it
   ```

2. **Environment Variables**: Use your existing Supabase configuration:
   ```bash
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_KEY=your-service-key-here
   ```

### Option B: Use Direct PostgreSQL Connection

If you want to use a direct PostgreSQL connection instead of Supabase:

1. **Database Setup**: Create a PostgreSQL database and run the migration:
   ```sql
   -- Connect to your PostgreSQL database and run:
   -- migration/complete_setup.sql
   ```

2. **Environment Variables**: Use direct PostgreSQL connection:
   ```bash
   DATABASE_URL=postgresql://username:password@host:port/database
   ```

## Step 2: Coolify Deployment Configuration

### Environment Variables for Coolify

Add these environment variables to your Coolify deployment:

```bash
# Database Configuration (choose one option)

# Option A: Supabase (your current setup)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key-here

# Option B: Direct PostgreSQL (alternative)
# DATABASE_URL=postgresql://username:password@host:port/database

# Service Ports
ARCHON_UI_PORT=3737
ARCHON_SERVER_PORT=8181
ARCHON_MCP_PORT=8051
ARCHON_AGENTS_PORT=8052

# Host Configuration
HOST=localhost

# Optional: AI Provider (can be set via UI later)
OPENAI_API_KEY=your-openai-api-key-here

# Optional: Logging
LOG_LEVEL=INFO
```

### Docker Compose Configuration

Create a `docker-compose.yml` file for Coolify:

```yaml
version: '3.8'

services:
  # Server Service (FastAPI + Socket.IO + Crawling)
  archon-server:
    build:
      context: ./python
      dockerfile: Dockerfile.server
    container_name: archon-server
    ports:
      - "${ARCHON_SERVER_PORT:-8181}:${ARCHON_SERVER_PORT:-8181}"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
      - ARCHON_SERVER_PORT=${ARCHON_SERVER_PORT:-8181}
      - ARCHON_MCP_PORT=${ARCHON_MCP_PORT:-8051}
      - ARCHON_AGENTS_PORT=${ARCHON_AGENTS_PORT:-8052}
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    networks:
      - archon-network

  # MCP Server Service
  archon-mcp:
    build:
      context: ./python
      dockerfile: Dockerfile.mcp
    container_name: archon-mcp
    ports:
      - "${ARCHON_MCP_PORT:-8051}:${ARCHON_MCP_PORT:-8051}"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - API_SERVICE_URL=http://archon-server:${ARCHON_SERVER_PORT:-8181}
      - AGENTS_SERVICE_URL=http://archon-agents:${ARCHON_AGENTS_PORT:-8052}
      - ARCHON_MCP_PORT=${ARCHON_MCP_PORT:-8051}
    depends_on:
      - archon-server
      - archon-agents
    networks:
      - archon-network

  # Agents Service
  archon-agents:
    build:
      context: ./python
      dockerfile: Dockerfile.agents
    container_name: archon-agents
    ports:
      - "${ARCHON_AGENTS_PORT:-8052}:${ARCHON_AGENTS_PORT:-8052}"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
      - ARCHON_AGENTS_PORT=${ARCHON_AGENTS_PORT:-8052}
    networks:
      - archon-network

  # Frontend UI
  archon-frontend:
    build: ./archon-ui-main
    container_name: archon-ui
    ports:
      - "${ARCHON_UI_PORT:-3737}:3737"
    environment:
      - VITE_API_URL=http://${HOST:-localhost}:${ARCHON_SERVER_PORT:-8181}
      - VITE_ARCHON_SERVER_PORT=${ARCHON_SERVER_PORT:-8181}
      - ARCHON_SERVER_PORT=${ARCHON_SERVER_PORT:-8181}
      - HOST=${HOST:-localhost}
    depends_on:
      - archon-server
    networks:
      - archon-network

networks:
  archon-network:
    driver: bridge
```

## Step 3: Deployment Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/coleam00/archon.git
   cd archon
   ```

2. **Database Migration**:
   - If using Supabase: Run `migration/complete_setup.sql` in your Supabase SQL Editor
   - If using PostgreSQL: Connect to your database and run the migration script

3. **Configure Environment Variables**:
   - Add the environment variables listed above to your Coolify deployment
   - Make sure to replace placeholder values with your actual credentials

4. **Deploy on Coolify**:
   - Upload the repository to Coolify
   - Configure the environment variables
   - Set the build context and Docker Compose file
   - Deploy the application

## Step 4: Post-Deployment Configuration

1. **Access the UI**: Navigate to `http://your-domain:3737`

2. **Configure API Keys**: 
   - Go to Settings → API Keys
   - Add your OpenAI API key or other LLM provider credentials

3. **Test the Setup**:
   - Try uploading a document
   - Test web crawling functionality
   - Verify MCP server connectivity

## Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   - Verify your `DATABASE_URL` or Supabase credentials
   - Check that the database is accessible from your Coolify instance
   - Ensure the migration script has been run

2. **Port Conflicts**:
   - Make sure the ports (3737, 8181, 8051, 8052) are not in use
   - Update the port configuration if needed

3. **Container Build Issues**:
   - Check that all required files are present
   - Verify Docker build context is correct
   - Check container logs for specific error messages

### Logs and Debugging

To view logs for specific services:
```bash
# Server logs
docker logs archon-server

# MCP server logs
docker logs archon-mcp

# Frontend logs
docker logs archon-ui
```

### Health Checks

Test the services:
```bash
# Server health
curl http://localhost:8181/health

# MCP server health
curl http://localhost:8051/health

# Frontend
curl http://localhost:3737
```

## Security Considerations

1. **Environment Variables**: Never commit sensitive credentials to version control
2. **Database Access**: Use strong passwords and limit database access
3. **Network Security**: Configure firewalls and network policies appropriately
4. **SSL/TLS**: Use HTTPS in production environments
5. **Service Keys**: Keep your Supabase service keys secure and never expose them in documentation

## Support

If you encounter issues:
1. Check the logs for error messages
2. Verify all environment variables are set correctly
3. Ensure the database migration has been completed
4. Check network connectivity between services

For additional help, refer to the main README.md or create an issue in the GitHub repository.
