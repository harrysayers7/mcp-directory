"""Unit tests for template MCP server tools."""

import pytest
from unittest.mock import Mock, AsyncMock
from mcp_common.exceptions import ValidationError

from servers.template.main import hello_world, get_info


@pytest.mark.asyncio
async def test_hello_world_success(mock_context):
    """Test successful hello_world tool execution."""
    result = await hello_world("Alice", mock_context)
    
    assert result["success"] is True
    assert result["data"]["greeting"] == "Hello, Alice!"
    assert result["message"] == "Greeting generated successfully"
    mock_context.info.assert_called()


@pytest.mark.asyncio
async def test_hello_world_default_name(mock_context):
    """Test hello_world with default name."""
    result = await hello_world(ctx=mock_context)
    
    assert result["success"] is True
    assert result["data"]["greeting"] == "Hello, World!"
    mock_context.info.assert_called()


@pytest.mark.asyncio
async def test_hello_world_empty_name():
    """Test hello_world with empty name raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        await hello_world("")
    
    assert "Name cannot be empty" in str(exc_info.value)


@pytest.mark.asyncio
async def test_hello_world_whitespace_name():
    """Test hello_world with whitespace-only name raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        await hello_world("   ")
    
    assert "Name cannot be empty" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_info_success(mock_context):
    """Test successful get_info tool execution."""
    result = await get_info("123", mock_context)
    
    assert result["success"] is True
    assert result["data"]["id"] == "123"
    assert result["data"]["name"] == "Item 123"
    assert result["data"]["status"] == "active"
    assert result["message"] == "Item information retrieved successfully"
    mock_context.info.assert_called()


@pytest.mark.asyncio
async def test_get_info_empty_id():
    """Test get_info with empty ID raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        await get_info("")
    
    assert "Item ID cannot be empty" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_info_whitespace_id():
    """Test get_info with whitespace-only ID raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        await get_info("   ")
    
    assert "Item ID cannot be empty" in str(exc_info.value)
