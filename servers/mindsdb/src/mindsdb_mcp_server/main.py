"""Main MindsDB MCP Server implementation."""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional

import redis.asyncio as redis
import structlog
from fastmcp import FastMCP
from mcp import Tool

from .config import config
from .tools import (
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

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer() if config.log_format == "json" else structlog.dev.ConsoleRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Initialize FastMCP server
mcp = FastMCP("MindsDB MCP Server")

# Global Redis client for caching
redis_client: Optional[redis.Redis] = None


async def init_redis():
    """Initialize Redis client for caching."""
    global redis_client
    try:
        redis_client = redis.Redis(
            host=config.redis_host,
            port=config.redis_port,
            password=config.redis_password,
            db=config.redis_db,
            decode_responses=True,
        )
        # Test connection
        await redis_client.ping()
        logger.info("Connected to Redis", host=config.redis_host, port=config.redis_port)
    except Exception as e:
        logger.warning("Failed to connect to Redis, caching disabled", error=str(e))
        redis_client = None


async def cleanup_redis():
    """Cleanup Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None
        logger.info("Disconnected from Redis")


@mcp.tool()
async def execute_sql_query_tool(
    query: str,
    context: Optional[Dict[str, Any]] = None,
    use_cache: bool = True,
) -> Dict[str, Any]:
    """Execute SQL query against MindsDB federated data sources.
    
    This tool allows you to run SQL queries against any data source connected to MindsDB,
    including databases, APIs, and files. MindsDB will automatically handle the connection
    and query execution across different data sources.
    
    Args:
        query: SQL query to execute (e.g., "SELECT * FROM mydb.mytable LIMIT 10")
        context: Optional context parameters for the query
        use_cache: Whether to use caching for improved performance
        
    Returns:
        Query results with data, columns, and metadata
    """
    return await execute_sql_query(query, context, use_cache)


@mcp.tool()
async def list_databases_tool(use_cache: bool = True) -> Dict[str, Any]:
    """List all available databases and data sources in MindsDB.
    
    This tool shows all the data sources that are currently connected to MindsDB,
    including databases, APIs, and file sources. Use this to discover what data
    is available for querying.
    
    Args:
        use_cache: Whether to use caching for improved performance
        
    Returns:
        List of available databases and their metadata
    """
    return await list_databases(use_cache)


@mcp.tool()
async def describe_table_tool(
    database: str,
    table: str,
    use_cache: bool = True,
) -> Dict[str, Any]:
    """Describe table schema and metadata.
    
    This tool provides detailed information about a table's structure, including
    column names, data types, and constraints. Use this to understand the schema
    before writing queries.
    
    Args:
        database: Database name
        table: Table name
        use_cache: Whether to use caching for improved performance
        
    Returns:
        Table schema information including columns and data types
    """
    return await describe_table(database, table, use_cache)


@mcp.tool()
async def get_table_sample_tool(
    database: str,
    table: str,
    limit: int = 10,
    use_cache: bool = True,
) -> Dict[str, Any]:
    """Get sample data from a table.
    
    This tool retrieves a sample of rows from a table, which is useful for
    understanding the data structure and content before writing more complex queries.
    
    Args:
        database: Database name
        table: Table name
        limit: Number of rows to return (1-1000)
        use_cache: Whether to use caching for improved performance
        
    Returns:
        Sample data with column information
    """
    return await get_table_sample(database, table, limit, use_cache)


@mcp.tool()
async def create_ml_model_tool(
    model_name: str,
    query: str,
    engine: str = "lightwood",
    target_column: Optional[str] = None,
    problem_type: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new machine learning model for training.
    
    This tool creates a new ML model in MindsDB that can be trained on your data.
    MindsDB supports various ML engines and can automatically determine the best
    approach for your specific problem.
    
    Args:
        model_name: Name of the model (must be unique)
        query: Training query that selects the data for training
        engine: ML engine to use (lightwood, sklearn, etc.)
        target_column: Target column for prediction (if not specified, MindsDB will infer)
        problem_type: Type of ML problem (regression, classification, time_series)
        
    Returns:
        Model creation result with status information
    """
    return await create_ml_model(
        model_name, query, engine, target_column, problem_type
    )


@mcp.tool()
async def make_prediction_tool(
    model_name: str,
    data: List[Dict[str, Any]],
    confidence_threshold: Optional[float] = None,
) -> Dict[str, Any]:
    """Make prediction using a trained model.
    
    This tool uses a trained model to make predictions on new data. You can provide
    single or multiple records for batch prediction.
    
    Args:
        model_name: Name of the trained model
        data: Input data for prediction (list of dictionaries)
        confidence_threshold: Confidence threshold for predictions (0.0-1.0)
        
    Returns:
        Prediction results with confidence scores
    """
    return await make_prediction(model_name, data, confidence_threshold)


@mcp.tool()
async def get_model_status_tool(model_name: str) -> Dict[str, Any]:
    """Get model training status and information.
    
    This tool provides information about a model's training status, accuracy,
    and other relevant metadata.
    
    Args:
        model_name: Name of the model
        
    Returns:
        Model status information including training progress and accuracy
    """
    return await get_model_status(model_name)


@mcp.tool()
async def evaluate_model_tool(
    model_name: str,
    test_data: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Evaluate model performance with metrics.
    
    This tool evaluates a trained model's performance using various metrics
    such as accuracy, precision, recall, and F1-score.
    
    Args:
        model_name: Name of the model to evaluate
        test_data: Optional test data for evaluation (if not provided, uses validation data)
        
    Returns:
        Model evaluation metrics and performance statistics
    """
    return await evaluate_model(model_name, test_data)


@mcp.tool()
async def forecast_time_series_tool(
    model_name: str,
    horizon: int = 10,
    frequency: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate time series forecast using trained model.
    
    This tool generates future predictions for time series data using a trained
    time series model. It's particularly useful for forecasting trends and patterns.
    
    Args:
        model_name: Name of the time series model
        horizon: Number of future periods to forecast (1-1000)
        frequency: Forecast frequency (daily, weekly, monthly, etc.)
        
    Returns:
        Time series forecast with future predictions
    """
    return await forecast_time_series(model_name, horizon, frequency)


# Resource definitions
@mcp.resource("mindsdb://databases")
async def get_databases_resource() -> List[Dict[str, Any]]:
    """Get list of available databases as a resource."""
    result = await list_databases()
    if result.get("success"):
        return result.get("databases", [])
    return []


@mcp.resource("mindsdb://models")
async def get_models_resource() -> List[Dict[str, Any]]:
    """Get list of available models as a resource."""
    # This would require a separate API call to list models
    # For now, return empty list
    return []


# Prompt templates
@mcp.prompt()
async def analyze_data_prompt(
    database: str,
    table: str,
    question: str,
) -> str:
    """Generate a prompt for data analysis tasks.
    
    Args:
        database: Database name
        table: Table name
        question: Analysis question
        
    Returns:
        Formatted prompt for data analysis
    """
    return f"""
You are a data analyst working with the {database}.{table} table in MindsDB.

Question: {question}

To answer this question, you can:
1. First, explore the table structure using describe_table
2. Get sample data using get_table_sample to understand the data
3. Write SQL queries using execute_sql_query to analyze the data
4. Create visualizations or summaries as needed

Available tools:
- describe_table: Get table schema
- get_table_sample: Get sample data
- execute_sql_query: Run SQL queries
- list_databases: See all available data sources

Start by exploring the table structure and sample data to understand what's available.
"""


@mcp.prompt()
async def create_ml_model_prompt(
    problem_description: str,
    data_source: str,
) -> str:
    """Generate a prompt for creating ML models.
    
    Args:
        problem_description: Description of the ML problem
        data_source: Data source to use for training
        
    Returns:
        Formatted prompt for ML model creation
    """
    return f"""
You are a machine learning engineer working with MindsDB to create a predictive model.

Problem: {problem_description}
Data Source: {data_source}

To create this model, you should:
1. First explore the data using list_databases and describe_table
2. Get sample data to understand the structure
3. Identify the target variable for prediction
4. Create the model using create_ml_model with appropriate parameters
5. Monitor training progress with get_model_status
6. Evaluate the model performance with evaluate_model

Available tools:
- list_databases: See available data sources
- describe_table: Understand data structure
- get_table_sample: Explore sample data
- create_ml_model: Create and train the model
- get_model_status: Monitor training
- evaluate_model: Assess performance

Start by exploring the data to understand what's available for training.
"""


async def main():
    """Main entry point for the MindsDB MCP Server."""
    logger.info("Starting MindsDB MCP Server", version=config.mcp_server_version)
    
    # Initialize Redis for caching
    await init_redis()
    
    try:
        # Run the MCP server
        await mcp.run()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down")
    except Exception as e:
        logger.error("Server error", error=str(e))
        sys.exit(1)
    finally:
        # Cleanup
        await cleanup_redis()
        logger.info("MindsDB MCP Server stopped")


if __name__ == "__main__":
    # Check if running on Railway (has PORT env var)
    if os.getenv("PORT"):
        # Run web server for Railway deployment
        from .web_server import app
        import uvicorn
        port = int(os.getenv("PORT", 8000))
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        # Run MCP server directly for local development
        asyncio.run(main())
