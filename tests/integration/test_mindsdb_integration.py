"""Integration tests for MindsDB MCP Server."""

import pytest
import asyncio
import httpx
from unittest.mock import AsyncMock, patch

from mindsdb_mcp_server.main import mcp
from mindsdb_mcp_server.client import MindsDBClient
from mindsdb_mcp_server.tools import (
    execute_sql_query,
    list_databases,
    create_ml_model,
    make_prediction,
)


class TestMindsDBIntegration:
    """Integration tests for MindsDB MCP Server."""

    @pytest.fixture
    def mindsdb_url(self):
        """Get MindsDB URL from environment or use default."""
        import os
        host = os.getenv("MINDSDB_HOST", "http://localhost")
        port = os.getenv("MINDSDB_PORT", "47334")
        return f"{host}:{port}"

    @pytest.fixture
    def mindsdb_client(self, mindsdb_url):
        """Create MindsDB client for integration tests."""
        return MindsDBClient(
            api_key="test-key",
            host=mindsdb_url,
            port=47334,
        )

    @pytest.mark.asyncio
    async def test_mindsdb_connection(self, mindsdb_client):
        """Test connection to MindsDB service."""
        try:
            async with mindsdb_client as client:
                # Test basic connectivity
                response = await client._make_request("GET", "status")
                assert response is not None
        except httpx.ConnectError:
            pytest.skip("MindsDB service not available for integration testing")

    @pytest.mark.asyncio
    async def test_list_databases_integration(self, mindsdb_url):
        """Test listing databases with real MindsDB service."""
        try:
            result = await list_databases(use_cache=False)
            assert result["success"] is True
            assert "databases" in result
            assert isinstance(result["databases"], list)
        except Exception as e:
            if "Connection" in str(e):
                pytest.skip("MindsDB service not available for integration testing")
            else:
                raise

    @pytest.mark.asyncio
    async def test_execute_sql_integration(self, mindsdb_url):
        """Test SQL execution with real MindsDB service."""
        try:
            # Test a simple query that should work
            result = await execute_sql_query("SELECT 1 as test_column", use_cache=False)
            assert result["success"] is True
            assert "data" in result
            assert "columns" in result
            assert result["row_count"] >= 0
        except Exception as e:
            if "Connection" in str(e):
                pytest.skip("MindsDB service not available for integration testing")
            else:
                raise

    @pytest.mark.asyncio
    async def test_mcp_tools_registration(self):
        """Test that MCP tools are properly registered."""
        # Get all registered tools from the MCP server
        tools = mcp.list_tools()
        tool_names = [tool.name for tool in tools]
        
        expected_tools = [
            "execute_sql_query_tool",
            "list_databases_tool",
            "describe_table_tool",
            "get_table_sample_tool",
            "create_ml_model_tool",
            "make_prediction_tool",
            "get_model_status_tool",
            "evaluate_model_tool",
            "forecast_time_series_tool",
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names

    @pytest.mark.asyncio
    async def test_mcp_resources_registration(self):
        """Test that MCP resources are properly registered."""
        # Get all registered resources from the MCP server
        resources = mcp.list_resources()
        resource_uris = [resource.uri for resource in resources]
        
        expected_resources = [
            "mindsdb://databases",
            "mindsdb://models",
        ]
        
        for expected_resource in expected_resources:
            assert expected_resource in resource_uris

    @pytest.mark.asyncio
    async def test_mcp_prompts_registration(self):
        """Test that MCP prompts are properly registered."""
        # Get all registered prompts from the MCP server
        prompts = mcp.list_prompts()
        prompt_names = [prompt.name for prompt in prompts]
        
        expected_prompts = [
            "analyze_data_prompt",
            "create_ml_model_prompt",
        ]
        
        for expected_prompt in expected_prompts:
            assert expected_prompt in prompt_names

    @pytest.mark.asyncio
    async def test_redis_caching_integration(self):
        """Test Redis caching integration."""
        try:
            import redis.asyncio as redis
            
            # Create Redis client
            redis_client = redis.Redis(
                host="localhost",
                port=6379,
                decode_responses=True,
            )
            
            # Test Redis connection
            await redis_client.ping()
            
            # Test cache operations
            test_key = "test_cache_key"
            test_data = {"test": "data"}
            
            await redis_client.setex(test_key, 60, '{"test": "data"}')
            cached_data = await redis_client.get(test_key)
            
            assert cached_data is not None
            
            # Cleanup
            await redis_client.delete(test_key)
            await redis_client.close()
            
        except Exception as e:
            if "Connection" in str(e):
                pytest.skip("Redis service not available for integration testing")
            else:
                raise

    @pytest.mark.asyncio
    async def test_error_handling_integration(self, mindsdb_url):
        """Test error handling with real service."""
        try:
            # Test with invalid query
            result = await execute_sql_query("INVALID SQL QUERY", use_cache=False)
            assert result["success"] is False
            assert "error" in result
            assert result["query"] == "INVALID SQL QUERY"
        except Exception as e:
            if "Connection" in str(e):
                pytest.skip("MindsDB service not available for integration testing")
            else:
                raise

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, mindsdb_url):
        """Test handling of concurrent requests."""
        try:
            # Create multiple concurrent requests
            tasks = [
                execute_sql_query("SELECT 1 as test", use_cache=False)
                for _ in range(5)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check that all requests completed (successfully or with expected errors)
            for result in results:
                if isinstance(result, Exception):
                    if "Connection" in str(result):
                        pytest.skip("MindsDB service not available for integration testing")
                    else:
                        raise result
                else:
                    assert "success" in result
                    
        except Exception as e:
            if "Connection" in str(e):
                pytest.skip("MindsDB service not available for integration testing")
            else:
                raise

    @pytest.mark.asyncio
    async def test_ml_model_workflow_integration(self, mindsdb_url):
        """Test complete ML model workflow with real service."""
        try:
            # This test would require a real MindsDB instance with data
            # For now, we'll test the error handling for missing data
            result = await create_ml_model(
                "test_integration_model",
                "SELECT * FROM non_existent_table",
                "lightwood"
            )
            
            # Should fail gracefully due to non-existent table
            assert result["success"] is False
            assert "error" in result
            
        except Exception as e:
            if "Connection" in str(e):
                pytest.skip("MindsDB service not available for integration testing")
            else:
                raise

    @pytest.mark.asyncio
    async def test_configuration_loading(self):
        """Test that configuration is loaded correctly."""
        from mindsdb_mcp_server.config import config
        
        # Test that configuration has expected values
        assert config.mcp_server_name == "mindsdb"
        assert config.mcp_server_version == "0.1.0"
        assert config.query_timeout == 300
        assert config.cache_ttl == 3600
        assert config.redis_host == "localhost"
        assert config.redis_port == 6379

    @pytest.mark.asyncio
    async def test_logging_configuration(self):
        """Test that logging is configured correctly."""
        import structlog
        from mindsdb_mcp_server.config import config
        
        # Test that structured logging is configured
        logger = structlog.get_logger(__name__)
        
        # Test logging levels
        assert config.log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        assert config.log_format in ["json", "text"]
        
        # Test that logger can be used without errors
        logger.info("Test log message", test_field="test_value")
