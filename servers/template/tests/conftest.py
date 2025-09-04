"""Pytest configuration for template MCP server tests."""

import pytest
from unittest.mock import Mock, AsyncMock
from fastmcp import FastMCP


@pytest.fixture
def mock_context():
    """Mock MCP context for testing."""
    context = Mock()
    context.info = AsyncMock()
    context.error = AsyncMock()
    context.warning = AsyncMock()
    return context


@pytest.fixture
def mcp_server():
    """MCP server instance for testing."""
    from servers.template.main import mcp
    return mcp


@pytest.fixture
def sample_tool_request():
    """Sample tool request for testing."""
    return {
        "tool_name": "hello_world",
        "parameters": {"name": "Test User"},
        "request_id": "test-request-123",
    }


@pytest.fixture
def sample_resource_uri():
    """Sample resource URI for testing."""
    return "template://item/123456"
