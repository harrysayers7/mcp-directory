"""Configuration management for MindsDB MCP Server."""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class MindsDBConfig(BaseSettings):
    """Configuration settings for MindsDB MCP Server."""

    # MindsDB Connection Settings
    mindsdb_api_key: Optional[str] = Field(
        default=None,
        description="MindsDB API key for authentication",
        env="MINDSDB_API_KEY",
    )
    mindsdb_host: str = Field(
        default="https://cloud.mindsdb.com",
        description="MindsDB host URL",
        env="MINDSDB_HOST",
    )
    mindsdb_port: int = Field(
        default=47334,
        description="MindsDB port",
        env="MINDSDB_PORT",
    )
    
    # MCP Server Settings
    mcp_server_name: str = Field(
        default="mindsdb",
        description="Name of the MCP server",
        env="MCP_SERVER_NAME",
    )
    mcp_server_version: str = Field(
        default="0.1.0",
        description="Version of the MCP server",
        env="MCP_SERVER_VERSION",
    )
    
    # Performance Settings
    max_connections: int = Field(
        default=10,
        description="Maximum number of concurrent connections",
        env="MAX_CONNECTIONS",
    )
    query_timeout: int = Field(
        default=300,
        description="Query timeout in seconds",
        env="QUERY_TIMEOUT",
    )
    cache_ttl: int = Field(
        default=3600,
        description="Cache TTL in seconds",
        env="CACHE_TTL",
    )
    
    # Redis Cache Settings
    redis_host: str = Field(
        default="localhost",
        description="Redis host for caching",
        env="REDIS_HOST",
    )
    redis_port: int = Field(
        default=6379,
        description="Redis port",
        env="REDIS_PORT",
    )
    redis_password: Optional[str] = Field(
        default=None,
        description="Redis password",
        env="REDIS_PASSWORD",
    )
    redis_db: int = Field(
        default=0,
        description="Redis database number",
        env="REDIS_DB",
    )
    
    # Logging Settings
    log_level: str = Field(
        default="INFO",
        description="Logging level",
        env="LOG_LEVEL",
    )
    log_format: str = Field(
        default="json",
        description="Log format (json or text)",
        env="LOG_FORMAT",
    )
    
    # Security Settings
    enable_auth: bool = Field(
        default=True,
        description="Enable authentication",
        env="ENABLE_AUTH",
    )
    allowed_origins: list[str] = Field(
        default=["*"],
        description="Allowed CORS origins",
        env="ALLOWED_ORIGINS",
    )
    
    # Rate Limiting
    rate_limit_requests: int = Field(
        default=100,
        description="Rate limit requests per minute",
        env="RATE_LIMIT_REQUESTS",
    )
    rate_limit_window: int = Field(
        default=60,
        description="Rate limit window in seconds",
        env="RATE_LIMIT_WINDOW",
    )

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global configuration instance
config = MindsDBConfig()
