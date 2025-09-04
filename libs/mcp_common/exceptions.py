"""
Custom exceptions for MCP servers.

Provides a hierarchy of exceptions for different error types and scenarios.
"""

from typing import Any, Dict, Optional


class MCPError(Exception):
    """Base exception for all MCP-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize MCP error.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary."""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details,
        }


class ValidationError(MCPError):
    """Raised when input validation fails."""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs,
    ) -> None:
        """Initialize validation error.
        
        Args:
            message: Error message
            field: Field that failed validation
            value: Value that failed validation
            **kwargs: Additional error details
        """
        details = kwargs.copy()
        if field is not None:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)
        
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class AuthenticationError(MCPError):
    """Raised when authentication fails."""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        auth_type: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Initialize authentication error.
        
        Args:
            message: Error message
            auth_type: Type of authentication that failed
            **kwargs: Additional error details
        """
        details = kwargs.copy()
        if auth_type is not None:
            details["auth_type"] = auth_type
        
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            details=details,
        )


class AuthorizationError(MCPError):
    """Raised when authorization fails."""
    
    def __init__(
        self,
        message: str = "Authorization failed",
        required_permission: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Initialize authorization error.
        
        Args:
            message: Error message
            required_permission: Permission that was required
            **kwargs: Additional error details
        """
        details = kwargs.copy()
        if required_permission is not None:
            details["required_permission"] = required_permission
        
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            details=details,
        )


class RateLimitError(MCPError):
    """Raised when rate limit is exceeded."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        limit: Optional[int] = None,
        window: Optional[int] = None,
        retry_after: Optional[int] = None,
        **kwargs,
    ) -> None:
        """Initialize rate limit error.
        
        Args:
            message: Error message
            limit: Rate limit that was exceeded
            window: Time window for the limit
            retry_after: Seconds to wait before retrying
            **kwargs: Additional error details
        """
        details = kwargs.copy()
        if limit is not None:
            details["limit"] = limit
        if window is not None:
            details["window"] = window
        if retry_after is not None:
            details["retry_after"] = retry_after
        
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            details=details,
        )


class ExternalServiceError(MCPError):
    """Raised when external service calls fail."""
    
    def __init__(
        self,
        message: str,
        service: Optional[str] = None,
        status_code: Optional[int] = None,
        **kwargs,
    ) -> None:
        """Initialize external service error.
        
        Args:
            message: Error message
            service: Name of the external service
            status_code: HTTP status code if applicable
            **kwargs: Additional error details
        """
        details = kwargs.copy()
        if service is not None:
            details["service"] = service
        if status_code is not None:
            details["status_code"] = status_code
        
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details,
        )


class ConfigurationError(MCPError):
    """Raised when configuration is invalid or missing."""
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Initialize configuration error.
        
        Args:
            message: Error message
            config_key: Configuration key that caused the error
            **kwargs: Additional error details
        """
        details = kwargs.copy()
        if config_key is not None:
            details["config_key"] = config_key
        
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            details=details,
        )


class DatabaseError(MCPError):
    """Raised when database operations fail."""
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        table: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Initialize database error.
        
        Args:
            message: Error message
            operation: Database operation that failed
            table: Table involved in the operation
            **kwargs: Additional error details
        """
        details = kwargs.copy()
        if operation is not None:
            details["operation"] = operation
        if table is not None:
            details["table"] = table
        
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details=details,
        )


class NotFoundError(MCPError):
    """Raised when a requested resource is not found."""
    
    def __init__(
        self,
        message: str = "Resource not found",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Initialize not found error.
        
        Args:
            message: Error message
            resource_type: Type of resource not found
            resource_id: ID of resource not found
            **kwargs: Additional error details
        """
        details = kwargs.copy()
        if resource_type is not None:
            details["resource_type"] = resource_type
        if resource_id is not None:
            details["resource_id"] = resource_id
        
        super().__init__(
            message=message,
            error_code="NOT_FOUND_ERROR",
            details=details,
        )


class ConflictError(MCPError):
    """Raised when a resource conflict occurs."""
    
    def __init__(
        self,
        message: str = "Resource conflict",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Initialize conflict error.
        
        Args:
            message: Error message
            resource_type: Type of resource in conflict
            resource_id: ID of resource in conflict
            **kwargs: Additional error details
        """
        details = kwargs.copy()
        if resource_type is not None:
            details["resource_type"] = resource_type
        if resource_id is not None:
            details["resource_id"] = resource_id
        
        super().__init__(
            message=message,
            error_code="CONFLICT_ERROR",
            details=details,
        )


class TimeoutError(MCPError):
    """Raised when an operation times out."""
    
    def __init__(
        self,
        message: str = "Operation timed out",
        timeout: Optional[float] = None,
        operation: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Initialize timeout error.
        
        Args:
            message: Error message
            timeout: Timeout value in seconds
            operation: Operation that timed out
            **kwargs: Additional error details
        """
        details = kwargs.copy()
        if timeout is not None:
            details["timeout"] = timeout
        if operation is not None:
            details["operation"] = operation
        
        super().__init__(
            message=message,
            error_code="TIMEOUT_ERROR",
            details=details,
        )


class UnauthorizedError(MCPError):
    """Unauthorized error (401)."""
    
    def __init__(self, message: str = "Unauthorized", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="UNAUTHORIZED",
            details=details,
        )


class ForbiddenError(MCPError):
    """Forbidden error (403)."""
    
    def __init__(self, message: str = "Forbidden", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="FORBIDDEN",
            details=details,
        )


class InternalServerError(MCPError):
    """Internal server error (500)."""
    
    def __init__(self, message: str = "Internal server error", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="INTERNAL_SERVER_ERROR",
            details=details,
        )
