"""
Tool utilities for MCP servers.
"""

from typing import Any, Dict, List, Optional, Callable, Type
from abc import ABC, abstractmethod
import asyncio
import time
from functools import wraps

from .exceptions import MCPError, ValidationError
from .models import ToolRequest, ToolResponse


class BaseMCPTool(ABC):
    """Base class for MCP tools."""
    
    def __init__(self, name: str, description: str):
        """Initialize base MCP tool."""
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters."""
        pass
    
    def validate_parameters(self, **kwargs) -> None:
        """Validate tool parameters."""
        # Override in subclasses for specific validation
        pass


class ToolRegistry:
    """Registry for MCP tools."""
    
    def __init__(self):
        """Initialize tool registry."""
        self._tools: Dict[str, BaseMCPTool] = {}
    
    def register(self, tool: BaseMCPTool) -> None:
        """Register a tool."""
        self._tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[BaseMCPTool]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self._tools.keys())
    
    def execute_tool(self, name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool by name."""
        tool = self.get_tool(name)
        if not tool:
            raise MCPError(f"Tool '{name}' not found")
        
        try:
            tool.validate_parameters(**kwargs)
            return asyncio.run(tool.execute(**kwargs))
        except Exception as e:
            raise MCPError(f"Tool execution failed: {str(e)}")


def tool_execution_time(func: Callable) -> Callable:
    """Decorator to measure tool execution time."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            raise e
    return wrapper


def validate_tool_input(data: Dict[str, Any], required_fields: List[str]) -> None:
    """Validate tool input data."""
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"Required field '{field}' is missing")
        
        if data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
            raise ValidationError(f"Field '{field}' cannot be empty")


def create_tool_response(
    success: bool,
    data: Any = None,
    message: str = "",
    error: Optional[str] = None,
    execution_time: float = 0.0,
    request_id: Optional[str] = None
) -> ToolResponse:
    """Create a standardized tool response."""
    return ToolResponse(
        success=success,
        result=data,
        error=error,
        execution_time=execution_time,
        request_id=request_id,
        message=message
    )
