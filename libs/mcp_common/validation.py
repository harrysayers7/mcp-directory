"""
Validation utilities for MCP servers.
"""

import re
from typing import Any, Type, Union, List, Dict, Optional
from email_validator import validate_email, EmailNotValidError

from .exceptions import ValidationError


def validate_input(
    value: Any,
    expected_type: Type,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    pattern: Optional[str] = None,
    required: bool = True
) -> Any:
    """Validate input value with type and constraints."""
    
    if value is None:
        if required:
            raise ValidationError("Value is required")
        return None
    
    # Type validation
    if not isinstance(value, expected_type):
        raise ValidationError(
            f"Expected {expected_type.__name__}, got {type(value).__name__}"
        )
    
    # String-specific validations
    if isinstance(value, str):
        # Length validation
        if min_length is not None and len(value) < min_length:
            raise ValidationError(f"Value too short (minimum {min_length} characters)")
        
        if max_length is not None and len(value) > max_length:
            raise ValidationError(f"Value too long (maximum {max_length} characters)")
        
        # Pattern validation
        if pattern and not re.match(pattern, value):
            raise ValidationError(f"Value does not match required pattern")
        
        # Trim whitespace
        value = value.strip()
        
        # Check if empty after trimming
        if not value and required:
            raise ValidationError("Value cannot be empty")
    
    return value


def validate_email_address(email: str) -> str:
    """Validate email address format."""
    try:
        validated_email = validate_email(email)
        return validated_email.email
    except EmailNotValidError as e:
        raise ValidationError(f"Invalid email address: {str(e)}")


def validate_url(url: str) -> str:
    """Validate URL format."""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(url):
        raise ValidationError("Invalid URL format")
    
    return url


def validate_uuid(uuid_string: str) -> str:
    """Validate UUID format."""
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    
    if not uuid_pattern.match(uuid_string):
        raise ValidationError("Invalid UUID format")
    
    return uuid_string


def validate_positive_integer(value: Any) -> int:
    """Validate positive integer."""
    try:
        int_value = int(value)
        if int_value <= 0:
            raise ValidationError("Value must be positive")
        return int_value
    except (ValueError, TypeError):
        raise ValidationError("Value must be a positive integer")


def validate_non_negative_integer(value: Any) -> int:
    """Validate non-negative integer."""
    try:
        int_value = int(value)
        if int_value < 0:
            raise ValidationError("Value must be non-negative")
        return int_value
    except (ValueError, TypeError):
        raise ValidationError("Value must be a non-negative integer")


def validate_enum(value: Any, enum_class: Type) -> Any:
    """Validate enum value."""
    if value not in enum_class:
        valid_values = [e.value for e in enum_class]
        raise ValidationError(f"Invalid value. Must be one of: {valid_values}")
    return value


def validate_list_length(
    value: List[Any],
    min_length: Optional[int] = None,
    max_length: Optional[int] = None
) -> List[Any]:
    """Validate list length."""
    if min_length is not None and len(value) < min_length:
        raise ValidationError(f"List too short (minimum {min_length} items)")
    
    if max_length is not None and len(value) > max_length:
        raise ValidationError(f"List too long (maximum {max_length} items)")
    
    return value


def validate_dict_keys(
    value: Dict[str, Any],
    required_keys: List[str],
    optional_keys: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Validate dictionary keys."""
    missing_keys = [key for key in required_keys if key not in value]
    if missing_keys:
        raise ValidationError(f"Missing required keys: {missing_keys}")
    
    if optional_keys:
        invalid_keys = [
            key for key in value.keys()
            if key not in required_keys + optional_keys
        ]
        if invalid_keys:
            raise ValidationError(f"Invalid keys: {invalid_keys}")
    
    return value


def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """Sanitize string input."""
    # Remove control characters
    sanitized = ''.join(char for char in value if ord(char) >= 32 or char in '\t\n\r')
    
    # Trim whitespace
    sanitized = sanitized.strip()
    
    # Limit length
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def validate_output(data: Any, expected_type: Type = None) -> Any:
    """Validate output data."""
    if expected_type and not isinstance(data, expected_type):
        raise ValidationError(f"Expected {expected_type.__name__}, got {type(data).__name__}")
    return data
