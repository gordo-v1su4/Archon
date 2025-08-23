# Archon + Supabase Integration Guide

This guide will help you integrate Archon into your existing Supabase stack in Coolify.

## 🎯 Integration Strategy

Instead of running Archon as a separate application, we'll add it as services to your existing Supabase stack. This approach:

- ✅ Shares the same database (your existing Supabase PostgreSQL)
- ✅ Uses the same network and environment variables
- ✅ Leverages your existing Kong gateway for routing
- ✅ Maintains a single deployment unit

## 📋 Prerequisites

- ✅ Your Supabase stack is already running in Coolify
- ✅ GitHub Actions workflow is set up and working
- ✅ Database migration has been run (migration/complete_setup.sql)

## 🔧 Step 1: Database Migration

First, ensure the Archon database schema is added to your existing Supabase database:

1. **Access your Supabase Studio** (usually at `https://your-domain`)
2. **Go to SQL Editor**
3. **Run the migration script**:
   ```sql
   -- Copy and paste the contents of migration/complete_setup.sql
   -- This will add all the necessary tables for Archon
   ```

## 🔧 Step 2: Add Archon Services to Your Docker Compose

You have two options:

### Option A: Add Services to Existing Compose File

1. **In Coolify**, go to your Supabase project
2. **Edit the Docker Compose file**
3. **Add the Archon services** from `docker-compose.coolify-integrated.yml`
4. **Add the Kong routes** (see Kong configuration below)

### Option B: Use the Integrated Compose File

1. **Replace your existing Docker Compose** with the integrated version
2. **Merge the services** from both files
3. **Update environment variables** as needed

## 🔧 Step 3: Kong Gateway Configuration

Add these routes to your existing Kong configuration (in the kong.yml section):

```yaml
# Add these services to your existing services section:

## Archon API routes
- name: archon-api
  url: http://archon-server:8181
  routes:
    - name: archon-api-all
      strip_path: true
      paths:
        - /archon/api/
  plugins:
    - name: cors
    - name: key-auth
      config:
        hide_credentials: true
    - name: acl
      config:
        hide_groups_header: true
        allow:
          - admin
          - anon

## Archon MCP routes
- name: archon-mcp
  url: http://archon-mcp:8051
  routes:
    - name: archon-mcp-all
      strip_path: true
      paths:
        - /archon/mcp/
  plugins:
    - name: cors

## Archon Agents routes
- name: archon-agents
  url: http://archon-agents:8052
  routes:
    - name: archon-agents-all
      strip_path: true
      paths:
        - /archon/agents/
  plugins:
    - name: cors
    - name: key-auth
      config:
        hide_credentials: true
    - name: acl
      config:
        hide_groups_header: true
        allow:
          - admin
          - anon
```

## 🔧 Step 4: Environment Variables

Add these environment variables to your Coolify deployment:

```bash
# Archon-specific variables
OPENAI_API_KEY=your-openai-api-key-here

# The following should already exist in your Supabase stack:
# SERVICE_SUPABASESERVICE_KEY
# SERVICE_PASSWORD_POSTGRES
# POSTGRES_DB
# POSTGRES_HOSTNAME
# POSTGRES_PORT
```

## 🔧 Step 5: Deploy and Test

1. **Commit and push** your changes to GitHub
2. **GitHub Actions** will trigger the build
3. **Coolify** will receive the webhook and rebuild
4. **Monitor the deployment** in Coolify dashboard

## 🌐 Access Points

After deployment, you'll have access to:

- **Archon UI**: `https://your-domain:3737` (direct port access)
- **Archon API**: `https://your-domain/archon/api/` (via Kong)
- **Archon MCP**: `https://your-domain/archon/mcp/` (via Kong)
- **Archon Agents**: `https://your-domain/archon/agents/` (via Kong)
- **Supabase Studio**: `https://your-domain/` (existing)

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   - Verify `SERVICE_SUPABASESERVICE_KEY` is set correctly
   - Check that the migration script has been run
   - Ensure Archon services can reach `supabase-kong:8000`

2. **Port Conflicts**:
   - Ports 3737, 8181, 8051, 8052 should not conflict with existing services
   - If conflicts occur, update the port mappings

3. **Build Failures**:
   - Check that all Dockerfiles exist in the correct locations
   - Verify the build context paths are correct
   - Check container logs for specific errors

### Health Checks

Test the services:
```bash
# Archon Server
curl http://localhost:8181/health

# Archon MCP
curl http://localhost:8051/health

# Archon Agents
curl http://localhost:8052/health

# Archon UI
curl http://localhost:3737
```

### Logs

View logs for Archon services:
```bash
# In Coolify dashboard or via Docker
docker logs archon-server
docker logs archon-mcp
docker logs archon-agents
docker logs archon-ui
```

## 🔄 CI/CD Integration

Your existing GitHub Actions workflow will:

1. **Build Archon images** when you push changes
2. **Trigger Coolify webhook** to rebuild the stack
3. **Deploy all services** (Supabase + Archon) together

## 🎉 Next Steps

After successful deployment:

1. **Configure API Keys** in the Archon UI
2. **Test document upload** functionality
3. **Verify MCP server** connectivity
4. **Test web crawling** features

## 📞 Support

If you encounter issues:

1. Check the logs for specific error messages
2. Verify all environment variables are set correctly
3. Ensure the database migration has been completed
4. Check network connectivity between services

The integration should provide a seamless experience with Archon running alongside your existing Supabase stack!
