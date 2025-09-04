"""MindsDB client for MCP server integration."""

import asyncio
import json
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta

import httpx
import redis.asyncio as redis
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog

from .config import config

logger = structlog.get_logger(__name__)


class MindsDBClient:
    """Client for interacting with MindsDB API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        redis_client: Optional[redis.Redis] = None,
    ):
        """Initialize MindsDB client.
        
        Args:
            api_key: MindsDB API key
            host: MindsDB host URL
            port: MindsDB port
            redis_client: Redis client for caching
        """
        self.api_key = api_key or config.mindsdb_api_key
        self.host = host or config.mindsdb_host
        self.port = port or config.mindsdb_port
        self.redis_client = redis_client
        
        # Build base URL
        if self.host.startswith("http"):
            self.base_url = f"{self.host}:{self.port}"
        else:
            self.base_url = f"https://{self.host}:{self.port}"
        
        # HTTP client configuration
        self.timeout = httpx.Timeout(config.query_timeout)
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": f"mindsdb-mcp-server/{config.mcp_server_version}",
        }
        
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
        
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def connect(self):
        """Initialize HTTP client connection."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.headers,
                timeout=self.timeout,
            )
            logger.info("Connected to MindsDB", host=self.host, port=self.port)

    async def close(self):
        """Close HTTP client connection."""
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.info("Disconnected from MindsDB")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
    )
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request to MindsDB API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            
        Returns:
            Response data as dictionary
            
        Raises:
            httpx.HTTPError: If request fails
        """
        if not self._client:
            await self.connect()
        
        url = f"/api/{endpoint.lstrip('/')}"
        
        try:
            response = await self._client.request(
                method=method,
                url=url,
                json=data,
                params=params,
            )
            response.raise_for_status()
            return response.json()
        
        except httpx.HTTPError as e:
            logger.error(
                "MindsDB API request failed",
                method=method,
                endpoint=endpoint,
                error=str(e),
                status_code=getattr(e.response, 'status_code', None),
            )
            raise

    async def _get_cache_key(self, operation: str, **kwargs) -> str:
        """Generate cache key for operation.
        
        Args:
            operation: Operation name
            **kwargs: Operation parameters
            
        Returns:
            Cache key string
        """
        key_data = {
            "operation": operation,
            "params": sorted(kwargs.items()),
            "api_key": self.api_key[:8] + "..." if self.api_key else None,
        }
        return f"mindsdb:{hash(json.dumps(key_data, sort_keys=True))}"

    async def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get data from cache.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached data or None
        """
        if not self.redis_client:
            return None
        
        try:
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning("Failed to get from cache", error=str(e))
        
        return None

    async def _set_cache(self, cache_key: str, data: Dict[str, Any], ttl: int = None):
        """Set data in cache.
        
        Args:
            cache_key: Cache key
            data: Data to cache
            ttl: Time to live in seconds
        """
        if not self.redis_client:
            return
        
        try:
            ttl = ttl or config.cache_ttl
            await self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(data, default=str),
            )
        except Exception as e:
            logger.warning("Failed to set cache", error=str(e))

    async def execute_sql(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """Execute SQL query against MindsDB.
        
        Args:
            query: SQL query string
            context: Optional context parameters
            use_cache: Whether to use caching
            
        Returns:
            Query results
        """
        cache_key = None
        if use_cache:
            cache_key = await self._get_cache_key("execute_sql", query=query, context=context)
            cached_result = await self._get_from_cache(cache_key)
            if cached_result:
                logger.info("Returning cached SQL result", query=query[:100])
                return cached_result

        data = {"query": query}
        if context:
            data["context"] = context

        result = await self._make_request("POST", "sql/query", data=data)
        
        if use_cache and cache_key:
            await self._set_cache(cache_key, result)
        
        logger.info("Executed SQL query", query=query[:100], rows=len(result.get("data", [])))
        return result

    async def list_databases(self, use_cache: bool = True) -> Dict[str, Any]:
        """List all available databases.
        
        Args:
            use_cache: Whether to use caching
            
        Returns:
            List of databases
        """
        cache_key = None
        if use_cache:
            cache_key = await self._get_cache_key("list_databases")
            cached_result = await self._get_from_cache(cache_key)
            if cached_result:
                logger.info("Returning cached databases list")
                return cached_result

        result = await self._make_request("GET", "databases")
        
        if use_cache and cache_key:
            await self._set_cache(cache_key, result, ttl=300)  # Cache for 5 minutes
        
        logger.info("Listed databases", count=len(result.get("data", [])))
        return result

    async def describe_table(
        self,
        database: str,
        table: str,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """Describe table schema.
        
        Args:
            database: Database name
            table: Table name
            use_cache: Whether to use caching
            
        Returns:
            Table schema information
        """
        cache_key = None
        if use_cache:
            cache_key = await self._get_cache_key("describe_table", database=database, table=table)
            cached_result = await self._get_from_cache(cache_key)
            if cached_result:
                logger.info("Returning cached table description", database=database, table=table)
                return cached_result

        query = f"DESCRIBE {database}.{table}"
        result = await self.execute_sql(query, use_cache=False)
        
        if use_cache and cache_key:
            await self._set_cache(cache_key, result, ttl=600)  # Cache for 10 minutes
        
        logger.info("Described table", database=database, table=table)
        return result

    async def get_table_sample(
        self,
        database: str,
        table: str,
        limit: int = 10,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """Get sample data from table.
        
        Args:
            database: Database name
            table: Table name
            limit: Number of rows to return
            use_cache: Whether to use caching
            
        Returns:
            Sample data
        """
        cache_key = None
        if use_cache:
            cache_key = await self._get_cache_key(
                "get_table_sample",
                database=database,
                table=table,
                limit=limit,
            )
            cached_result = await self._get_from_cache(cache_key)
            if cached_result:
                logger.info("Returning cached table sample", database=database, table=table)
                return cached_result

        query = f"SELECT * FROM {database}.{table} LIMIT {limit}"
        result = await self.execute_sql(query, use_cache=False)
        
        if use_cache and cache_key:
            await self._set_cache(cache_key, result, ttl=300)  # Cache for 5 minutes
        
        logger.info("Got table sample", database=database, table=table, limit=limit)
        return result

    async def create_model(
        self,
        model_name: str,
        query: str,
        engine: str = "lightwood",
        **kwargs,
    ) -> Dict[str, Any]:
        """Create a new ML model.
        
        Args:
            model_name: Name of the model
            query: Training query
            engine: ML engine to use
            **kwargs: Additional model parameters
            
        Returns:
            Model creation result
        """
        data = {
            "name": model_name,
            "query": query,
            "engine": engine,
            **kwargs,
        }

        result = await self._make_request("POST", "models", data=data)
        logger.info("Created model", model_name=model_name, engine=engine)
        return result

    async def make_prediction(
        self,
        model_name: str,
        data: List[Dict[str, Any]],
        **kwargs,
    ) -> Dict[str, Any]:
        """Make prediction using trained model.
        
        Args:
            model_name: Name of the model
            data: Input data for prediction
            **kwargs: Additional prediction parameters
            
        Returns:
            Prediction results
        """
        prediction_data = {
            "data": data,
            **kwargs,
        }

        result = await self._make_request(
            "POST",
            f"models/{model_name}/predict",
            data=prediction_data,
        )
        logger.info("Made prediction", model_name=model_name, rows=len(data))
        return result

    async def get_model_status(self, model_name: str) -> Dict[str, Any]:
        """Get model training status.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model status information
        """
        result = await self._make_request("GET", f"models/{model_name}")
        logger.info("Got model status", model_name=model_name)
        return result

    async def evaluate_model(
        self,
        model_name: str,
        test_data: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Evaluate model performance.
        
        Args:
            model_name: Name of the model
            test_data: Optional test data
            
        Returns:
            Model evaluation metrics
        """
        data = {}
        if test_data:
            data["test_data"] = test_data

        result = await self._make_request(
            "POST",
            f"models/{model_name}/evaluate",
            data=data,
        )
        logger.info("Evaluated model", model_name=model_name)
        return result

    async def forecast_time_series(
        self,
        model_name: str,
        horizon: int = 10,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate time series forecast.
        
        Args:
            model_name: Name of the time series model
            horizon: Number of future periods to forecast
            **kwargs: Additional forecast parameters
            
        Returns:
            Forecast results
        """
        data = {
            "horizon": horizon,
            **kwargs,
        }

        result = await self._make_request(
            "POST",
            f"models/{model_name}/forecast",
            data=data,
        )
        logger.info("Generated forecast", model_name=model_name, horizon=horizon)
        return result
