"""
Configuration management for MCP servers.

Provides centralized configuration management with environment variable support.
"""

import os
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Config(BaseSettings):
    """Base configuration class for MCP servers."""
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Server Configuration
    host: str = Field(default="localhost", description="Server host")
    port: int = Field(default=8000, description="Server port")
    debug: bool = Field(default=False, description="Debug mode")
    environment: str = Field(default="development", description="Environment")
    
    # Security Configuration
    secret_key: str = Field(default="your-secret-key-change-this", description="Secret key for JWT")
    jwt_expiration: int = Field(default=3600, description="JWT expiration in seconds")
    cors_origins: List[str] = Field(default=["*"], description="CORS allowed origins")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", description="Log level")
    log_format: str = Field(default="json", description="Log format")
    
    # Database Configuration
    database_url: Optional[str] = Field(default=None, description="Database URL")
    
    # External API Configuration
    notion_api_key: Optional[str] = Field(default=None, description="Notion API key")
    github_token: Optional[str] = Field(default=None, description="GitHub token")
    supabase_url: Optional[str] = Field(default=None, description="Supabase URL")
    supabase_key: Optional[str] = Field(default=None, description="Supabase key")
    
    # Rate Limiting Configuration
    rate_limit_requests: int = Field(default=100, description="Rate limit requests per window")
    rate_limit_window: int = Field(default=3600, description="Rate limit window in seconds")
    rate_limit_burst: int = Field(default=10, description="Rate limit burst allowance")
    
    # Monitoring Configuration
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    metrics_port: int = Field(default=9090, description="Metrics port")
    
    # Health Check Configuration
    health_check_interval: int = Field(default=30, description="Health check interval in seconds")
    health_check_timeout: int = Field(default=5, description="Health check timeout in seconds")
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of: {valid_levels}")
        return v.upper()
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment."""
        valid_envs = ["development", "staging", "production", "test"]
        if v.lower() not in valid_envs:
            raise ValueError(f"Invalid environment. Must be one of: {valid_envs}")
        return v.lower()
    
    def get_database_url(self) -> str:
        """Get database URL with fallback."""
        if self.database_url:
            return self.database_url
        
        # Fallback to environment variable
        return os.getenv("DATABASE_URL", "sqlite:///./mcp.db")
    
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment.lower() == "production"
    
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment.lower() == "development"
    
    def get_cors_origins(self) -> List[str]:
        """Get CORS origins."""
        if "*" in self.cors_origins and self.is_production():
            # In production, don't allow all origins
            return ["https://yourdomain.com"]
        return self.cors_origins


@lru_cache()
def get_config() -> Config:
    """Get cached configuration instance."""
    return Config()


def get_database_config() -> Dict[str, Any]:
    """Get database configuration."""
    config = get_config()
    return {
        "url": config.get_database_url(),
        "echo": config.debug,
        "pool_size": 10,
        "max_overflow": 20,
    }


def get_redis_config() -> Dict[str, Any]:
    """Get Redis configuration."""
    return {
        "host": os.getenv("REDIS_HOST", "localhost"),
        "port": int(os.getenv("REDIS_PORT", "6379")),
        "db": int(os.getenv("REDIS_DB", "0")),
        "password": os.getenv("REDIS_PASSWORD"),
    }


def get_logging_config() -> Dict[str, Any]:
    """Get logging configuration."""
    config = get_config()
    return {
        "level": config.log_level,
        "format": config.log_format,
        "handlers": ["console", "file"] if config.is_production() else ["console"],
    }