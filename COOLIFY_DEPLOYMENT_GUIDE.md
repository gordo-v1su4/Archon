# Coolify Deployment Guide for Archon

## Setting Up Webhooks in Coolify

### Step 1: Create the Webhook in Coolify

1. **Log into your Coolify dashboard**
2. **Navigate to your Archon application**
3. **Go to the "Webhooks" section**
4. **Create a new webhook** with these settings:
   - Type: `GitHub`
   - Events: `Push` (for automatic deployments on push)
   - Branch filter: `main` or `master` (depending on your default branch)

### Step 2: Configure GitHub Repository Secrets

You need to add the Coolify webhook URL to your GitHub repository secrets:

1. **Go to your GitHub repository**: https://github.com/gordo-v1su4/Archon
2. **Navigate to Settings → Secrets and variables → Actions**
3. **Add these repository secrets**:

```
COOLIFY_WEBHOOK_URL = https://your-coolify-instance.com/webhooks/deploy/YOUR_WEBHOOK_TOKEN
COOLIFY_APP_URL = https://your-deployed-app.com  # Optional, for health checks
```

### Step 3: Coolify Application Configuration

In your Coolify application settings, configure the following:

#### Docker Compose Configuration
Since you have a `docker-compose.yaml` file, use these settings in Coolify:

1. **Source**: GitHub Repository
2. **Repository**: `https://github.com/gordo-v1su4/Archon.git`
3. **Branch**: `main`
4. **Build Type**: `Docker Compose`
5. **Docker Compose File**: `docker-compose.yaml`

#### Environment Variables in Coolify
Add these environment variables in Coolify's application settings:

```bash
# Required - Add these in Coolify's environment variables section
SUPABASE_URL=your_supabase_url_here
SUPABASE_SERVICE_KEY=your_supabase_service_key_here

# Optional
OPENAI_API_KEY=your_openai_api_key_here
LOG_LEVEL=INFO
LOGFIRE_TOKEN=your_logfire_token_here

# Service Ports (these should match your docker-compose.yaml)
ARCHON_SERVER_PORT=8181
ARCHON_MCP_PORT=8051
ARCHON_AGENTS_PORT=8052

# Frontend Configuration
VITE_API_URL=http://your-coolify-domain.com:8181
VITE_ARCHON_SERVER_PORT=8181
HOST=0.0.0.0
```

### Step 4: Network Configuration in Coolify

Configure the exposed ports in Coolify:

1. **Main Application Port**: `3737` (Frontend)
2. **Additional Ports to Expose**:
   - `8181` - Archon Server (API + Socket.IO)
   - `8051` - MCP Server (optional, if you need external access)
   - `8052` - Agents Service (optional, if you need external access)

### Step 5: Webhook Payload Format

The webhook should send this payload format (already configured in your workflows):

```json
{
  "branch": "main",
  "commit": "SHA_HERE",
  "repository": "gordo-v1su4/Archon",
  "trigger": "github_push"
}
```

## Troubleshooting Webhook Issues

### 1. Test the Webhook Manually

Test if your webhook URL is working:

```bash
# Windows PowerShell
$body = @{
    branch = "main"
    commit = "test123"
    repository = "gordo-v1su4/Archon"
    trigger = "manual_test"
} | ConvertTo-Json

Invoke-RestMethod -Uri "YOUR_COOLIFY_WEBHOOK_URL" -Method Post -Body $body -ContentType "application/json"

# Or using curl (Git Bash/WSL)
curl -X POST "YOUR_COOLIFY_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"branch":"main","commit":"test123","repository":"gordo-v1su4/Archon","trigger":"manual_test"}'
```

### 2. Check GitHub Actions Logs

View the workflow runs to see if the webhook is being triggered:

```bash
# Go to: https://github.com/gordo-v1su4/Archon/actions
```

### 3. Common Webhook Issues and Solutions

#### Issue: 404 Not Found
**Solution**: Verify the webhook URL format. It should be:
```
https://your-coolify-instance.com/webhooks/deploy/YOUR_TOKEN
```

#### Issue: 401 Unauthorized
**Solution**: Check that the webhook token in the URL matches what Coolify generated.

#### Issue: Build Fails in Coolify
**Solution**: Check these common causes:

1. **Missing environment variables** - Ensure all required env vars are set in Coolify
2. **Port conflicts** - Make sure the ports aren't already in use
3. **Docker build context issues** - Verify all files referenced in Dockerfiles exist
4. **Memory limits** - Increase resource limits in Coolify if builds are failing

### 4. Verify Docker Images Build Locally

Before deploying to Coolify, ensure everything builds locally:

```bash
# Build all services locally
docker-compose build

# Or build individual services
docker build -f python/Dockerfile.server -t archon-server:test ./python
docker build -f python/Dockerfile.mcp -t archon-mcp:test ./python
docker build -f python/Dockerfile.agents -t archon-agents:test ./python
docker build -f archon-ui-main/Dockerfile -t archon-frontend:test ./archon-ui-main
```

### 5. Coolify-Specific Docker Compose Adjustments

You might need to create a `docker-compose.coolify.yaml` with Coolify-specific overrides:

```yaml
# docker-compose.coolify.yaml
services:
  archon-server:
    environment:
      - VITE_API_URL=${COOLIFY_URL}:8181
    networks:
      - coolify
      
  archon-frontend:
    environment:
      - VITE_API_URL=${COOLIFY_URL}:8181
      - HOST=0.0.0.0
    networks:
      - coolify

networks:
  coolify:
    external: true
```

### 6. GitHub Actions Webhook Trigger

Ensure your GitHub Actions workflow is correctly configured:

```yaml
# .github/workflows/deploy-coolify-simple.yml
name: Deploy to Coolify

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Coolify Deployment
        run: |
          curl -X POST "${{ secrets.COOLIFY_WEBHOOK_URL }}" \
            -H "Content-Type: application/json" \
            -d '{
              "branch": "${{ github.ref_name }}",
              "commit": "${{ github.sha }}",
              "repository": "${{ github.repository }}"
            }'
```

## Alternative: Direct GitHub Integration

Instead of using webhooks, you can configure Coolify to pull directly from GitHub:

1. **In Coolify**, go to your application settings
2. **Set up GitHub integration**:
   - Repository: `https://github.com/gordo-v1su4/Archon`
   - Branch: `main`
   - Enable "Auto Deploy on Push"
3. **Add a Deploy Key** (if repository is private):
   - Generate SSH key in Coolify
   - Add the public key to your GitHub repo's Deploy Keys

## Debugging Steps

1. **Check Coolify Logs**:
   - Application logs
   - Build logs
   - Deployment logs

2. **Verify Network Connectivity**:
   - Can Coolify reach GitHub?
   - Can GitHub webhooks reach Coolify?
   - Are firewall rules configured correctly?

3. **Test Each Service Individually**:
   ```bash
   # Test if services are running
   curl http://your-coolify-domain:8181/health  # Server
   curl http://your-coolify-domain:8051/health  # MCP
   curl http://your-coolify-domain:8052/health  # Agents
   curl http://your-coolify-domain:3737          # Frontend
   ```

## Need More Help?

If you're still having issues:

1. Share the specific error messages from Coolify's build/deployment logs
2. Check the GitHub Actions workflow run logs
3. Verify all environment variables are correctly set in Coolify
4. Ensure your Supabase instance is accessible from Coolify's network

Let me know what specific error you're encountering and I can provide more targeted assistance!
