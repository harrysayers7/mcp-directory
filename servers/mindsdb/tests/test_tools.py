"""Tests for MCP tools."""

import pytest
from unittest.mock import AsyncMock, patch

from mindsdb_mcp_server.tools import (
    execute_sql_query,
    list_databases,
    describe_table,
    get_table_sample,
    create_ml_model,
    make_prediction,
    get_model_status,
    evaluate_model,
    forecast_time_series,
    get_tools,
)


class TestMCPTools:
    """Test cases for MCP tools."""

    @pytest.mark.asyncio
    async def test_execute_sql_query_success(self):
        """Test successful SQL query execution."""
        mock_result = {
            "data": [{"id": 1, "name": "test"}],
            "columns": ["id", "name"],
        }
        
        with patch("mindsdb_mcp_server.tools.MindsDBClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.execute_sql.return_value = mock_result
            
            result = await execute_sql_query("SELECT * FROM test")
            
            assert result["success"] is True
            assert result["data"] == mock_result["data"]
            assert result["columns"] == mock_result["columns"]
            assert result["row_count"] == 1
            assert result["query"] == "SELECT * FROM test"

    @pytest.mark.asyncio
    async def test_execute_sql_query_error(self):
        """Test SQL query execution error handling."""
        with patch("mindsdb_mcp_server.tools.MindsDBClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.execute_sql.side_effect = Exception("Connection failed")
            
            result = await execute_sql_query("SELECT * FROM test")
            
            assert result["success"] is False
            assert "Connection failed" in result["error"]
            assert result["query"] == "SELECT * FROM test"

    @pytest.mark.asyncio
    async def test_list_databases_success(self):
        """Test successful database listing."""
        mock_result = {"data": [{"name": "db1"}, {"name": "db2"}]}
        
        with patch("mindsdb_mcp_server.tools.MindsDBClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.list_databases.return_value = mock_result
            
            result = await list_databases()
            
            assert result["success"] is True
            assert result["databases"] == mock_result["data"]
            assert result["count"] == 2

    @pytest.mark.asyncio
    async def test_list_databases_error(self):
        """Test database listing error handling."""
        with patch("mindsdb_mcp_server.tools.MindsDBClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.list_databases.side_effect = Exception("API error")
            
            result = await list_databases()
            
            assert result["success"] is False
            assert "API error" in result["error"]

    @pytest.mark.asyncio
    async def test_describe_table_success(self):
        """Test successful table description."""
        mock_result = {
            "data": [{"Field": "id", "Type": "int"}, {"Field": "name", "Type": "varchar"}]
        }
        
        with patch("mindsdb_mcp_server.tools.MindsDBClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.describe_table.return_value = mock_result
            
            result = await describe_table("test_db", "test_table")
            
            assert result["success"] is True
            assert result["database"] == "test_db"
            assert result["table"] == "test_table"
            assert result["schema"] == mock_result["data"]
            assert result["columns"] == ["id", "name"]

    @pytest.mark.asyncio
    async def test_describe_table_error(self):
        """Test table description error handling."""
        with patch("mindsdb_mcp_server.tools.MindsDBClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.describe_table.side_effect = Exception("Table not found")
            
            result = await describe_table("test_db", "test_table")
            
            assert result["success"] is False
            assert "Table not found" in result["error"]
            assert result["database"] == "test_db"
            assert result["table"] == "test_table"

    @pytest.mark.asyncio
    async def test_get_table_sample_success(self):
        """Test successful table sample retrieval."""
        mock_result = {
            "data": [{"id": 1, "name": "test1"}, {"id": 2, "name": "test2"}],
            "columns": ["id", "name"],
        }
        
        with patch("mindsdb_mcp_server.tools.MindsDBClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_table_sample.return_value = mock_result
            
            result = await get_table_sample("test_db", "test_table", 5)
            
            assert result["success"] is True
            assert result["database"] == "test_db"
            assert result["table"] == "test_table"
            assert result["data"] == mock_result["data"]
            assert result["columns"] == mock_result["columns"]
            assert result["row_count"] == 2
            assert result["limit"] == 5

    @pytest.mark.asyncio
    async def test_create_ml_model_success(self):
        """Test successful ML model creation."""
        mock_result = {"status": "created"}
        
        with patch("mindsdb_mcp_server.tools.MindsDBClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.create_model.return_value = mock_result
            
            result = await create_ml_model(
                "test_model",
                "SELECT * FROM training_data",
                "lightwood",
                "price",
                "regression"
            )
            
            assert result["success"] is True
            assert result["model_name"] == "test_model"
            assert result["engine"] == "lightwood"
            assert result["status"] == "created"
            assert "created successfully" in result["message"]

    @pytest.mark.asyncio
    async def test_create_ml_model_error(self):
        """Test ML model creation error handling."""
        with patch("mindsdb_mcp_server.tools.MindsDBClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.create_model.side_effect = Exception("Invalid query")
            
            result = await create_ml_model("test_model", "INVALID QUERY")
            
            assert result["success"] is False
            assert "Invalid query" in result["error"]
            assert result["model_name"] == "test_model"

    @pytest.mark.asyncio
    async def test_make_prediction_success(self):
        """Test successful prediction."""
        mock_result = {"data": [{"prediction": 100, "confidence": 0.95}]}
        test_data = [{"feature1": 10, "feature2": 20}]
        
        with patch("mindsdb_mcp_server.tools.MindsDBClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.make_prediction.return_value = mock_result
            
            result = await make_prediction("test_model", test_data, 0.8)
            
            assert result["success"] is True
            assert result["model_name"] == "test_model"
            assert result["predictions"] == mock_result["data"]
            assert result["row_count"] == 1
            assert result["confidence_threshold"] == 0.8

    @pytest.mark.asyncio
    async def test_make_prediction_error(self):
        """Test prediction error handling."""
        test_data = [{"feature1": 10}]
        
        with patch("mindsdb_mcp_server.tools.MindsDBClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.make_prediction.side_effect = Exception("Model not found")
            
            result = await make_prediction("test_model", test_data)
            
            assert result["success"] is False
            assert "Model not found" in result["error"]
            assert result["model_name"] == "test_model"

    @pytest.mark.asyncio
    async def test_get_model_status_success(self):
        """Test successful model status retrieval."""
        mock_result = {
            "status": "completed",
            "accuracy": 0.95,
            "created_at": "2024-01-01T00:00:00Z",
        }
        
        with patch("mindsdb_mcp_server.tools.MindsDBClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_model_status.return_value = mock_result
            
            result = await get_model_status("test_model")
            
            assert result["success"] is True
            assert result["model_name"] == "test_model"
            assert result["status"] == "completed"
            assert result["accuracy"] == 0.95

    @pytest.mark.asyncio
    async def test_evaluate_model_success(self):
        """Test successful model evaluation."""
        mock_result = {
            "metrics": {"accuracy": 0.95, "precision": 0.90},
            "accuracy": 0.95,
            "precision": 0.90,
            "recall": 0.88,
            "f1_score": 0.89,
        }
        
        with patch("mindsdb_mcp_server.tools.MindsDBClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.evaluate_model.return_value = mock_result
            
            result = await evaluate_model("test_model")
            
            assert result["success"] is True
            assert result["model_name"] == "test_model"
            assert result["accuracy"] == 0.95
            assert result["precision"] == 0.90
            assert result["recall"] == 0.88
            assert result["f1_score"] == 0.89

    @pytest.mark.asyncio
    async def test_forecast_time_series_success(self):
        """Test successful time series forecasting."""
        mock_result = {
            "data": [
                {"forecast": 100, "date": "2024-02-01"},
                {"forecast": 105, "date": "2024-02-02"},
            ]
        }
        
        with patch("mindsdb_mcp_server.tools.MindsDBClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.forecast_time_series.return_value = mock_result
            
            result = await forecast_time_series("test_model", 10, "daily")
            
            assert result["success"] is True
            assert result["model_name"] == "test_model"
            assert result["forecast"] == mock_result["data"]
            assert result["horizon"] == 10
            assert result["frequency"] == "daily"
            assert result["periods"] == 2

    def test_get_tools(self):
        """Test getting list of MCP tools."""
        tools = get_tools()
        
        assert len(tools) == 9
        tool_names = [tool.name for tool in tools]
        
        expected_tools = [
            "execute_sql_query",
            "list_databases",
            "describe_table",
            "get_table_sample",
            "create_ml_model",
            "make_prediction",
            "get_model_status",
            "evaluate_model",
            "forecast_time_series",
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
