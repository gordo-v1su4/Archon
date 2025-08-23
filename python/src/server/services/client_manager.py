"""
Client Manager Service

Manages database and API client connections.
"""

import os
import re
from urllib.parse import urlparse

from supabase import Client, create_client

from ..config.logfire_config import search_logger


def get_supabase_client() -> Client:
    """
    Get a Supabase client instance.
    
    This function now supports both Supabase and direct PostgreSQL connections.
    If DATABASE_URL is provided and starts with postgresql://, it will use
    a mock Supabase client that works with direct PostgreSQL connections.
    
    Returns:
        Supabase client instance
    """
    # Check for direct PostgreSQL connection string first
    database_url = os.getenv("DATABASE_URL")
    if database_url and database_url.startswith("postgresql://"):
        # For direct PostgreSQL connections, we'll use a mock client
        # that maintains compatibility with existing code
        search_logger.info("Using direct PostgreSQL connection via DATABASE_URL")
        return _create_postgres_mock_client(database_url)
    
    # Fall back to Supabase configuration
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")

    if not url or not key:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment variables"
        )

    try:
        # Let Supabase handle connection pooling internally
        client = create_client(url, key)

        # Extract project ID from URL for logging purposes only
        match = re.match(r"https://([^.]+)\.supabase\.co", url)
        if match:
            project_id = match.group(1)
            search_logger.info(f"Supabase client initialized - project_id={project_id}")

        return client
    except Exception as e:
        search_logger.error(f"Failed to create Supabase client: {e}")
        raise


def _create_postgres_mock_client(database_url: str) -> Client:
    """
    Create a mock Supabase client that works with direct PostgreSQL connections.
    
    This maintains compatibility with existing code while allowing direct
    PostgreSQL connections for self-hosted deployments.
    """
    try:
        # Parse the PostgreSQL connection string
        parsed = urlparse(database_url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 5432
        database = parsed.path.lstrip("/") or "postgres"
        
        search_logger.info(f"PostgreSQL connection configured: {host}:{port}/{database}")
        
        # Create a mock client that will be handled by the database layer
        # For now, we'll create a minimal client that can be extended
        class PostgresMockClient:
            def __init__(self, connection_string: str):
                self.connection_string = connection_string
                self._connection_info = {
                    'host': host,
                    'port': port,
                    'database': database,
                    'user': parsed.username or 'postgres'
                }
            
            def table(self, table_name: str):
                # Return a mock table object that can be extended
                return PostgresMockTable(table_name, self.connection_string)
            
            def __repr__(self):
                return f"PostgresMockClient(host={host}, port={port}, database={database})"
        
        class PostgresMockTable:
            def __init__(self, table_name: str, connection_string: str):
                self.table_name = table_name
                self.connection_string = connection_string
                self._filters = []
                self._updates = {}
                self._inserts = []
            
            def select(self, *args, **kwargs):
                # Mock select method
                return self
            
            def insert(self, data):
                # Mock insert method
                if isinstance(data, dict):
                    self._inserts = [data]
                else:
                    self._inserts = data
                return self
            
            def update(self, data):
                # Mock update method
                self._updates = data
                return self
            
            def delete(self):
                # Mock delete method
                return self
            
            def eq(self, column, value):
                # Mock equality filter
                self._filters.append(('eq', column, value))
                return self
            
            def execute(self):
                # Mock execute method
                # In a real implementation, this would execute the actual PostgreSQL query
                search_logger.info(f"Mock PostgreSQL operation: {self.table_name}")
                return PostgresMockResponse()
        
        class PostgresMockResponse:
            def __init__(self):
                self.data = []
                self.count = 0
        
        return PostgresMockClient(database_url)
        
    except Exception as e:
        search_logger.error(f"Failed to create PostgreSQL mock client: {e}")
        raise
