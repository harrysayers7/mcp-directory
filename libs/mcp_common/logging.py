"""
Logging utilities for MCP servers.
"""

import logging
import sys
from typing import Optional, Dict, Any
from pathlib import Path

import structlog
from structlog.stdlib import LoggerFactory

from .config import get_config


def setup_logging(log_level: str = "INFO") -> None:
    """Set up structured logging for MCP servers."""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class MCPLogger:
    """Enhanced logger for MCP servers with context."""
    
    def __init__(self, name: str):
        """Initialize MCP logger."""
        self.logger = get_logger(name)
        self._context: Dict[str, Any] = {}
    
    def bind(self, **kwargs) -> "MCPLogger":
        """Bind context to logger."""
        new_logger = MCPLogger(self.logger.name)
        new_logger._context = {**self._context, **kwargs}
        return new_logger
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message with context."""
        self.logger.info(message, **{**self._context, **kwargs})
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message with context."""
        self.logger.warning(message, **{**self._context, **kwargs})
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message with context."""
        self.logger.error(message, **{**self._context, **kwargs})
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message with context."""
        self.logger.debug(message, **{**self._context, **kwargs})
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message with context."""
        self.logger.critical(message, **{**self._context, **kwargs})


def create_request_logger(request_id: str, user_id: Optional[str] = None) -> MCPLogger:
    """Create a logger with request context."""
    logger = MCPLogger("mcp.request")
    context = {"request_id": request_id}
    if user_id:
        context["user_id"] = user_id
    return logger.bind(**context)
