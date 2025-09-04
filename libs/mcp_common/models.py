"""
Pydantic models for MCP servers.

Provides base models and common response types for MCP server implementations.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator
from pydantic import ConfigDict


class BaseResponseModel(BaseModel):
    """Base model with common configuration."""
    
    model_config = ConfigDict(
        use_enum_values=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
        }
    )


class ErrorResponse(BaseResponseModel):
    """Standard error response model."""
    
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request ID for tracing")
    
    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, v: Union[str, datetime]) -> datetime:
        """Parse timestamp from string or datetime."""
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v


class SuccessResponse(BaseResponseModel):
    """Standard success response model."""
    
    success: bool = Field(True, description="Success indicator")
    message: str = Field(..., description="Success message")
    data: Optional[Any] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    request_id: Optional[str] = Field(None, description="Request ID for tracing")
    
    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, v: Union[str, datetime]) -> datetime:
        """Parse timestamp from string or datetime."""
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v


class PaginationParams(BaseResponseModel):
    """Pagination parameters."""
    
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Number of items per page")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: str = Field("asc", pattern="^(asc|desc)$", description="Sort order")
    
    @property
    def offset(self) -> int:
        """Calculate offset for pagination."""
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseResponseModel):
    """Paginated response model."""
    
    items: List[Any] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")
    
    @field_validator("total_pages", mode="after")
    @classmethod
    def calculate_total_pages(cls, v: int, info) -> int:
        """Calculate total pages."""
        values = info.data
        total = values.get("total", 0)
        page_size = values.get("page_size", 1)
        return (total + page_size - 1) // page_size
    
    @field_validator("has_next", mode="after")
    @classmethod
    def calculate_has_next(cls, v: bool, info) -> bool:
        """Calculate if there is a next page."""
        values = info.data
        page = values.get("page", 1)
        total_pages = values.get("total_pages", 1)
        return page < total_pages
    
    @field_validator("has_prev", mode="after")
    @classmethod
    def calculate_has_prev(cls, v: bool, info) -> bool:
        """Calculate if there is a previous page."""
        values = info.data
        page = values.get("page", 1)
        return page > 1


class HealthCheckResponse(BaseResponseModel):
    """Health check response model."""
    
    status: str = Field(..., description="Health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Environment")
    services: Dict[str, str] = Field(default_factory=dict, description="Service statuses")
    uptime: float = Field(..., description="Uptime in seconds")
    
    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, v: Union[str, datetime]) -> datetime:
        """Parse timestamp from string or datetime."""
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v


class RateLimitInfo(BaseResponseModel):
    """Rate limit information model."""
    
    limit: int = Field(..., description="Rate limit")
    remaining: int = Field(..., description="Remaining requests")
    reset_time: datetime = Field(..., description="Reset time")
    retry_after: Optional[int] = Field(None, description="Seconds to wait before retrying")
    
    @field_validator("reset_time", mode="before")
    @classmethod
    def parse_reset_time(cls, v: Union[str, datetime, int]) -> datetime:
        """Parse reset time from string, datetime, or timestamp."""
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        elif isinstance(v, int):
            return datetime.fromtimestamp(v)
        return v


class AuthenticationInfo(BaseResponseModel):
    """Authentication information model."""
    
    user_id: str = Field(..., description="User ID")
    username: Optional[str] = Field(None, description="Username")
    email: Optional[str] = Field(None, description="Email address")
    roles: List[str] = Field(default_factory=list, description="User roles")
    permissions: List[str] = Field(default_factory=list, description="User permissions")
    expires_at: Optional[datetime] = Field(None, description="Token expiration time")
    issued_at: datetime = Field(default_factory=datetime.utcnow, description="Token issue time")
    
    @field_validator("expires_at", "issued_at", mode="before")
    @classmethod
    def parse_datetime(cls, v: Union[str, datetime, None]) -> Optional[datetime]:
        """Parse datetime from string or datetime."""
        if v is None:
            return None
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v


class ToolRequest(BaseResponseModel):
    """Tool request model."""
    
    tool_name: str = Field(..., description="Name of the tool")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")
    request_id: Optional[str] = Field(None, description="Request ID for tracing")
    user_id: Optional[str] = Field(None, description="User ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Request timestamp")
    
    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, v: Union[str, datetime]) -> datetime:
        """Parse timestamp from string or datetime."""
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v


class ToolResponse(BaseResponseModel):
    """Tool response model."""
    
    success: bool = Field(..., description="Success indicator")
    result: Optional[Any] = Field(None, description="Tool result")
    error: Optional[str] = Field(None, description="Error message if failed")
    execution_time: float = Field(..., description="Execution time in seconds")
    request_id: Optional[str] = Field(None, description="Request ID for tracing")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    message: str = Field("", description="Response message")
    
    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, v: Union[str, datetime]) -> datetime:
        """Parse timestamp from string or datetime."""
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v


class ResourceInfo(BaseResponseModel):
    """Resource information model."""
    
    uri: str = Field(..., description="Resource URI")
    name: str = Field(..., description="Resource name")
    description: Optional[str] = Field(None, description="Resource description")
    mime_type: Optional[str] = Field(None, description="MIME type")
    size: Optional[int] = Field(None, description="Resource size in bytes")
    last_modified: Optional[datetime] = Field(None, description="Last modified time")
    etag: Optional[str] = Field(None, description="ETag for caching")
    
    @field_validator("last_modified", mode="before")
    @classmethod
    def parse_last_modified(cls, v: Union[str, datetime, None]) -> Optional[datetime]:
        """Parse last modified time from string or datetime."""
        if v is None:
            return None
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v


class PromptRequest(BaseResponseModel):
    """Prompt request model."""
    
    prompt: str = Field(..., description="Prompt text")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Prompt parameters")
    request_id: Optional[str] = Field(None, description="Request ID for tracing")
    user_id: Optional[str] = Field(None, description="User ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Request timestamp")
    
    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, v: Union[str, datetime]) -> datetime:
        """Parse timestamp from string or datetime."""
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v


class PromptResponse(BaseResponseModel):
    """Prompt response model."""
    
    success: bool = Field(..., description="Success indicator")
    result: Optional[str] = Field(None, description="Generated text")
    error: Optional[str] = Field(None, description="Error message if failed")
    execution_time: float = Field(..., description="Execution time in seconds")
    request_id: Optional[str] = Field(None, description="Request ID for tracing")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, v: Union[str, datetime]) -> datetime:
        """Parse timestamp from string or datetime."""
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v