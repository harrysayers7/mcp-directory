"""
MCP Common Library

A shared library providing common utilities, patterns, and helpers for MCP servers
in the MCP Directory monorepo.
"""

from .auth import AuthenticationManager, AuthConfig
from .config import Config, get_config
from .exceptions import (
    MCPError, 
    ValidationError, 
    AuthenticationError, 
    RateLimitError, 
    ExternalServiceError,
    NotFoundError,
    ConflictError,
    UnauthorizedError,
    ForbiddenError,
    InternalServerError,
    ConfigurationError
)
from .logging import setup_logging, get_logger
from .models import BaseModel, ErrorResponse, SuccessResponse
from .rate_limiting import RateLimiter, RateLimitConfig
from .tools import BaseMCPTool, ToolRegistry
from .validation import validate_input, validate_output

__version__ = "0.1.0"
__all__ = [
    # Authentication
    "AuthenticationManager",
    "AuthConfig",
    
    # Configuration
    "Config",
    "get_config",
    
    # Exceptions
    "MCPError",
    "ValidationError",
    "AuthenticationError",
    "RateLimitError",
    "ExternalServiceError",
    "NotFoundError",
    "ConflictError",
    "UnauthorizedError",
    "ForbiddenError",
    "InternalServerError",
    "ConfigurationError",
    
    # Logging
    "setup_logging",
    "get_logger",
    
    # Models
    "BaseModel",
    "ErrorResponse",
    "SuccessResponse",
    
    # Rate Limiting
    "RateLimiter",
    "RateLimitConfig",
    
    # Tools
    "BaseMCPTool",
    "ToolRegistry",
    
    # Validation
    "validate_input",
    "validate_output",
]
