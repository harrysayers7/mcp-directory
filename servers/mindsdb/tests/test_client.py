"""Tests for MindsDB client."""

import pytest
from unittest.mock import AsyncMock, patch
import httpx

from mindsdb_mcp_server.client import MindsDBClient
from mindsdb_mcp_server.config import config


class TestMindsDBClient:
    """Test cases for MindsDBClient."""

    @pytest.fixture
    def client(self):
        """Create a MindsDB client for testing."""
        return MindsDBClient(
            api_key="test-key",
            host="https://test.mindsdb.com",
            port=47334,
        )

    @pytest.mark.asyncio
    async def test_client_initialization(self, client):
        """Test client initialization."""
        assert client.api_key == "test-key"
        assert client.host == "https://test.mindsdb.com"
        assert client.port == 47334
        assert client.base_url == "https://test.mindsdb.com:47334"
        assert "Authorization" in client.headers
        assert client.headers["Authorization"] == "Bearer test-key"

    @pytest.mark.asyncio
    async def test_connect_and_close(self, client):
        """Test client connection and disconnection."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value = mock_instance
            
            await client.connect()
            assert client._client is not None
            mock_client.assert_called_once()
            
            await client.close()
            assert client._client is None
            mock_instance.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_sql_success(self, client):
        """Test successful SQL execution."""
        mock_response = {
            "data": [{"id": 1, "name": "test"}],
            "columns": ["id", "name"],
        }
        
        with patch.object(client, "_make_request", return_value=mock_response):
            result = await client.execute_sql("SELECT * FROM test")
            
            assert result == mock_response
            client._make_request.assert_called_once_with(
                "POST", "sql/query", data={"query": "SELECT * FROM test"}
            )

    @pytest.mark.asyncio
    async def test_execute_sql_with_context(self, client):
        """Test SQL execution with context."""
        mock_response = {"data": [], "columns": []}
        context = {"param1": "value1"}
        
        with patch.object(client, "_make_request", return_value=mock_response):
            result = await client.execute_sql("SELECT * FROM test", context)
            
            client._make_request.assert_called_once_with(
                "POST",
                "sql/query",
                data={"query": "SELECT * FROM test", "context": context},
            )

    @pytest.mark.asyncio
    async def test_execute_sql_error(self, client):
        """Test SQL execution error handling."""
        with patch.object(client, "_make_request", side_effect=httpx.HTTPError("Connection failed")):
            with pytest.raises(httpx.HTTPError):
                await client.execute_sql("SELECT * FROM test")

    @pytest.mark.asyncio
    async def test_list_databases(self, client):
        """Test listing databases."""
        mock_response = {"data": [{"name": "db1"}, {"name": "db2"}]}
        
        with patch.object(client, "_make_request", return_value=mock_response):
            result = await client.list_databases()
            
            assert result == mock_response
            client._make_request.assert_called_once_with("GET", "databases")

    @pytest.mark.asyncio
    async def test_describe_table(self, client):
        """Test describing table."""
        mock_response = {"data": [{"Field": "id", "Type": "int"}]}
        
        with patch.object(client, "execute_sql", return_value=mock_response):
            result = await client.describe_table("test_db", "test_table")
            
            assert result == mock_response
            client.execute_sql.assert_called_once_with(
                "DESCRIBE test_db.test_table", None, True
            )

    @pytest.mark.asyncio
    async def test_get_table_sample(self, client):
        """Test getting table sample."""
        mock_response = {"data": [{"id": 1}], "columns": ["id"]}
        
        with patch.object(client, "execute_sql", return_value=mock_response):
            result = await client.get_table_sample("test_db", "test_table", 5)
            
            assert result == mock_response
            client.execute_sql.assert_called_once_with(
                "SELECT * FROM test_db.test_table LIMIT 5", None, True
            )

    @pytest.mark.asyncio
    async def test_create_model(self, client):
        """Test creating ML model."""
        mock_response = {"status": "created"}
        
        with patch.object(client, "_make_request", return_value=mock_response):
            result = await client.create_model(
                "test_model",
                "SELECT * FROM training_data",
                "lightwood",
                target="price"
            )
            
            assert result == mock_response
            client._make_request.assert_called_once_with(
                "POST",
                "models",
                data={
                    "name": "test_model",
                    "query": "SELECT * FROM training_data",
                    "engine": "lightwood",
                    "target": "price",
                }
            )

    @pytest.mark.asyncio
    async def test_make_prediction(self, client):
        """Test making prediction."""
        mock_response = {"data": [{"prediction": 100}]}
        test_data = [{"feature1": 10, "feature2": 20}]
        
        with patch.object(client, "_make_request", return_value=mock_response):
            result = await client.make_prediction("test_model", test_data)
            
            assert result == mock_response
            client._make_request.assert_called_once_with(
                "POST",
                "models/test_model/predict",
                data={"data": test_data},
            )

    @pytest.mark.asyncio
    async def test_get_model_status(self, client):
        """Test getting model status."""
        mock_response = {"status": "completed", "accuracy": 0.95}
        
        with patch.object(client, "_make_request", return_value=mock_response):
            result = await client.get_model_status("test_model")
            
            assert result == mock_response
            client._make_request.assert_called_once_with("GET", "models/test_model")

    @pytest.mark.asyncio
    async def test_evaluate_model(self, client):
        """Test evaluating model."""
        mock_response = {"accuracy": 0.95, "precision": 0.90}
        test_data = [{"feature1": 10, "target": 1}]
        
        with patch.object(client, "_make_request", return_value=mock_response):
            result = await client.evaluate_model("test_model", test_data)
            
            assert result == mock_response
            client._make_request.assert_called_once_with(
                "POST",
                "models/test_model/evaluate",
                data={"test_data": test_data},
            )

    @pytest.mark.asyncio
    async def test_forecast_time_series(self, client):
        """Test time series forecasting."""
        mock_response = {"data": [{"forecast": 100, "date": "2024-02-01"}]}
        
        with patch.object(client, "_make_request", return_value=mock_response):
            result = await client.forecast_time_series("test_model", 10, frequency="daily")
            
            assert result == mock_response
            client._make_request.assert_called_once_with(
                "POST",
                "models/test_model/forecast",
                data={"horizon": 10, "frequency": "daily"},
            )

    @pytest.mark.asyncio
    async def test_cache_key_generation(self, client):
        """Test cache key generation."""
        key1 = await client._get_cache_key("test_op", param1="value1", param2="value2")
        key2 = await client._get_cache_key("test_op", param2="value2", param1="value1")
        
        # Should be the same regardless of parameter order
        assert key1 == key2

    @pytest.mark.asyncio
    async def test_context_manager(self, client):
        """Test client as context manager."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value = mock_instance
            
            async with client as c:
                assert c is client
                assert client._client is not None
            
            # Should be closed after context
            mock_instance.aclose.assert_called_once()
