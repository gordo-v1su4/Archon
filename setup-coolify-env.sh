#!/bin/bash

# Archon Coolify Environment Setup Script
# This script helps you generate the environment variables for Coolify deployment

echo "🚀 Archon Coolify Environment Setup"
echo "=================================="
echo ""

# Function to prompt for input with default value
prompt_with_default() {
    local prompt="$1"
    local default="$2"
    local var_name="$3"
    
    if [ -n "$default" ]; then
        read -p "$prompt [$default]: " input
        if [ -z "$input" ]; then
            input="$default"
        fi
    else
        read -p "$prompt: " input
    fi
    
    echo "$var_name=$input"
}

echo "📋 Database Configuration"
echo "------------------------"

# Check if user wants to use existing Supabase or direct PostgreSQL
echo "Choose your database configuration:"
echo "1. Use existing Supabase (recommended for your setup)"
echo "2. Use direct PostgreSQL connection"
read -p "Enter your choice (1 or 2): " db_choice

echo ""
echo "🔧 Environment Variables for Coolify:"
echo "====================================="
echo ""

if [ "$db_choice" = "2" ]; then
    # Direct PostgreSQL configuration
    echo "# Direct PostgreSQL Configuration"
    prompt_with_default "Enter PostgreSQL connection string" "postgresql://postgres:password@127.0.0.1:5432/postgres" "DATABASE_URL"
    echo ""
else
    # Supabase configuration (default)
    echo "# Supabase Configuration"
    prompt_with_default "Enter Supabase URL" "https://supabase.v1su4.com" "SUPABASE_URL"
    prompt_with_default "Enter Supabase Service Key" "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXBhYmFzZSIsImlhdCI6MTc1NTYzNDM4MCwiZXhwIjo0OTExMzA3OTgwLCJyb2xlIjoic2VydmljZV9yb2xlIn0.3Qf1E9JNswJQH-d1AXl4HKNKHSCEQbof0b5X582X54w" "SUPABASE_SERVICE_KEY"
    echo ""
fi

echo "# Service Ports"
prompt_with_default "Enter UI Port" "3737" "ARCHON_UI_PORT"
prompt_with_default "Enter Server Port" "8181" "ARCHON_SERVER_PORT"
prompt_with_default "Enter MCP Port" "8051" "ARCHON_MCP_PORT"
prompt_with_default "Enter Agents Port" "8052" "ARCHON_AGENTS_PORT"
echo ""

echo "# Host Configuration"
prompt_with_default "Enter Host" "localhost" "HOST"
echo ""

echo "# Optional: AI Provider (can be set via UI later)"
prompt_with_default "Enter OpenAI API Key (optional)" "" "OPENAI_API_KEY"
echo ""

echo "# Optional: Logging"
prompt_with_default "Enter Log Level" "INFO" "LOG_LEVEL"
echo ""

echo "✅ Environment variables generated!"
echo ""
echo "📝 Next Steps:"
echo "1. Copy the environment variables above to your Coolify deployment"
echo "2. Run the database migration: migration/complete_setup.sql"
echo "3. Deploy the application on Coolify"
echo "4. Access the UI at http://your-domain:3737"
echo ""
echo "📚 For detailed instructions, see COOLIFY_SETUP.md"
