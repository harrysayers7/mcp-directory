"""MCP tools for MindsDB integration."""

from typing import Any, Dict, List, Optional, Union
import asyncio
import json

from mcp import Tool
from pydantic import BaseModel, Field
import structlog

from .client import MindsDBClient
from .config import config

logger = structlog.get_logger(__name__)


# Tool Input Models
class ExecuteSQLQueryInput(BaseModel):
    """Input for SQL query execution."""
    query: str = Field(..., description="SQL query to execute")
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional context parameters for the query"
    )
    use_cache: bool = Field(
        default=True,
        description="Whether to use caching for the query"
    )


class ListDatabasesInput(BaseModel):
    """Input for listing databases."""
    use_cache: bool = Field(
        default=True,
        description="Whether to use caching"
    )


class DescribeTableInput(BaseModel):
    """Input for describing table schema."""
    database: str = Field(..., description="Database name")
    table: str = Field(..., description="Table name")
    use_cache: bool = Field(
        default=True,
        description="Whether to use caching"
    )


class GetTableSampleInput(BaseModel):
    """Input for getting table sample data."""
    database: str = Field(..., description="Database name")
    table: str = Field(..., description="Table name")
    limit: int = Field(
        default=10,
        ge=1,
        le=1000,
        description="Number of rows to return (1-1000)"
    )
    use_cache: bool = Field(
        default=True,
        description="Whether to use caching"
    )


class CreateMLModelInput(BaseModel):
    """Input for creating ML model."""
    model_name: str = Field(..., description="Name of the model")
    query: str = Field(..., description="Training query")
    engine: str = Field(
        default="lightwood",
        description="ML engine to use"
    )
    target_column: Optional[str] = Field(
        default=None,
        description="Target column for prediction"
    )
    problem_type: Optional[str] = Field(
        default=None,
        description="Type of ML problem (regression, classification, etc.)"
    )


class MakePredictionInput(BaseModel):
    """Input for making predictions."""
    model_name: str = Field(..., description="Name of the model")
    data: List[Dict[str, Any]] = Field(..., description="Input data for prediction")
    confidence_threshold: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confidence threshold for predictions"
    )


class GetModelStatusInput(BaseModel):
    """Input for getting model status."""
    model_name: str = Field(..., description="Name of the model")


class EvaluateModelInput(BaseModel):
    """Input for evaluating model."""
    model_name: str = Field(..., description="Name of the model")
    test_data: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Optional test data for evaluation"
    )


class ForecastTimeSeriesInput(BaseModel):
    """Input for time series forecasting."""
    model_name: str = Field(..., description="Name of the time series model")
    horizon: int = Field(
        default=10,
        ge=1,
        le=1000,
        description="Number of future periods to forecast"
    )
    frequency: Optional[str] = Field(
        default=None,
        description="Forecast frequency (daily, weekly, monthly, etc.)"
    )


# Tool Implementations
async def execute_sql_query(
    query: str,
    context: Optional[Dict[str, Any]] = None,
    use_cache: bool = True,
) -> Dict[str, Any]:
    """Execute SQL query against MindsDB.
    
    Args:
        query: SQL query to execute
        context: Optional context parameters
        use_cache: Whether to use caching
        
    Returns:
        Query results
    """
    async with MindsDBClient() as client:
        try:
            result = await client.execute_sql(query, context, use_cache)
            return {
                "success": True,
                "data": result.get("data", []),
                "columns": result.get("columns", []),
                "row_count": len(result.get("data", [])),
                "query": query,
            }
        except Exception as e:
            logger.error("SQL query execution failed", error=str(e), query=query)
            return {
                "success": False,
                "error": str(e),
                "query": query,
            }


async def list_databases(use_cache: bool = True) -> Dict[str, Any]:
    """List all available databases in MindsDB.
    
    Args:
        use_cache: Whether to use caching
        
    Returns:
        List of databases
    """
    async with MindsDBClient() as client:
        try:
            result = await client.list_databases(use_cache)
            databases = result.get("data", [])
            return {
                "success": True,
                "databases": databases,
                "count": len(databases),
            }
        except Exception as e:
            logger.error("Failed to list databases", error=str(e))
            return {
                "success": False,
                "error": str(e),
            }


async def describe_table(
    database: str,
    table: str,
    use_cache: bool = True,
) -> Dict[str, Any]:
    """Describe table schema and metadata.
    
    Args:
        database: Database name
        table: Table name
        use_cache: Whether to use caching
        
    Returns:
        Table schema information
    """
    async with MindsDBClient() as client:
        try:
            result = await client.describe_table(database, table, use_cache)
            return {
                "success": True,
                "database": database,
                "table": table,
                "schema": result.get("data", []),
                "columns": [col.get("Field", "") for col in result.get("data", [])],
            }
        except Exception as e:
            logger.error(
                "Failed to describe table",
                error=str(e),
                database=database,
                table=table,
            )
            return {
                "success": False,
                "error": str(e),
                "database": database,
                "table": table,
            }


async def get_table_sample(
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
    async with MindsDBClient() as client:
        try:
            result = await client.get_table_sample(database, table, limit, use_cache)
            return {
                "success": True,
                "database": database,
                "table": table,
                "data": result.get("data", []),
                "columns": result.get("columns", []),
                "row_count": len(result.get("data", [])),
                "limit": limit,
            }
        except Exception as e:
            logger.error(
                "Failed to get table sample",
                error=str(e),
                database=database,
                table=table,
            )
            return {
                "success": False,
                "error": str(e),
                "database": database,
                "table": table,
            }


async def create_ml_model(
    model_name: str,
    query: str,
    engine: str = "lightwood",
    target_column: Optional[str] = None,
    problem_type: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new machine learning model.
    
    Args:
        model_name: Name of the model
        query: Training query
        engine: ML engine to use
        target_column: Target column for prediction
        problem_type: Type of ML problem
        
    Returns:
        Model creation result
    """
    async with MindsDBClient() as client:
        try:
            kwargs = {}
            if target_column:
                kwargs["target"] = target_column
            if problem_type:
                kwargs["problem_type"] = problem_type
                
            result = await client.create_model(model_name, query, engine, **kwargs)
            return {
                "success": True,
                "model_name": model_name,
                "engine": engine,
                "status": "created",
                "message": f"Model '{model_name}' created successfully",
            }
        except Exception as e:
            logger.error(
                "Failed to create model",
                error=str(e),
                model_name=model_name,
            )
            return {
                "success": False,
                "error": str(e),
                "model_name": model_name,
            }


async def make_prediction(
    model_name: str,
    data: List[Dict[str, Any]],
    confidence_threshold: Optional[float] = None,
) -> Dict[str, Any]:
    """Make prediction using trained model.
    
    Args:
        model_name: Name of the model
        data: Input data for prediction
        confidence_threshold: Confidence threshold for predictions
        
    Returns:
        Prediction results
    """
    async with MindsDBClient() as client:
        try:
            kwargs = {}
            if confidence_threshold is not None:
                kwargs["confidence_threshold"] = confidence_threshold
                
            result = await client.make_prediction(model_name, data, **kwargs)
            return {
                "success": True,
                "model_name": model_name,
                "predictions": result.get("data", []),
                "row_count": len(data),
                "confidence_threshold": confidence_threshold,
            }
        except Exception as e:
            logger.error(
                "Failed to make prediction",
                error=str(e),
                model_name=model_name,
            )
            return {
                "success": False,
                "error": str(e),
                "model_name": model_name,
            }


async def get_model_status(model_name: str) -> Dict[str, Any]:
    """Get model training status and information.
    
    Args:
        model_name: Name of the model
        
    Returns:
        Model status information
    """
    async with MindsDBClient() as client:
        try:
            result = await client.get_model_status(model_name)
            return {
                "success": True,
                "model_name": model_name,
                "status": result.get("status", "unknown"),
                "accuracy": result.get("accuracy"),
                "created_at": result.get("created_at"),
                "updated_at": result.get("updated_at"),
            }
        except Exception as e:
            logger.error(
                "Failed to get model status",
                error=str(e),
                model_name=model_name,
            )
            return {
                "success": False,
                "error": str(e),
                "model_name": model_name,
            }


async def evaluate_model(
    model_name: str,
    test_data: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Evaluate model performance.
    
    Args:
        model_name: Name of the model
        test_data: Optional test data for evaluation
        
    Returns:
        Model evaluation metrics
    """
    async with MindsDBClient() as client:
        try:
            result = await client.evaluate_model(model_name, test_data)
            return {
                "success": True,
                "model_name": model_name,
                "metrics": result.get("metrics", {}),
                "accuracy": result.get("accuracy"),
                "precision": result.get("precision"),
                "recall": result.get("recall"),
                "f1_score": result.get("f1_score"),
            }
        except Exception as e:
            logger.error(
                "Failed to evaluate model",
                error=str(e),
                model_name=model_name,
            )
            return {
                "success": False,
                "error": str(e),
                "model_name": model_name,
            }


async def forecast_time_series(
    model_name: str,
    horizon: int = 10,
    frequency: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate time series forecast.
    
    Args:
        model_name: Name of the time series model
        horizon: Number of future periods to forecast
        frequency: Forecast frequency
        
    Returns:
        Forecast results
    """
    async with MindsDBClient() as client:
        try:
            kwargs = {}
            if frequency:
                kwargs["frequency"] = frequency
                
            result = await client.forecast_time_series(model_name, horizon, **kwargs)
            return {
                "success": True,
                "model_name": model_name,
                "forecast": result.get("data", []),
                "horizon": horizon,
                "frequency": frequency,
                "periods": len(result.get("data", [])),
            }
        except Exception as e:
            logger.error(
                "Failed to generate forecast",
                error=str(e),
                model_name=model_name,
            )
            return {
                "success": False,
                "error": str(e),
                "model_name": model_name,
            }


# MCP Tool Definitions
def get_tools() -> List[Tool]:
    """Get list of MCP tools for MindsDB integration.
    
    Returns:
        List of MCP tools
    """
    return [
        Tool(
            name="execute_sql_query",
            description="Execute SQL query against MindsDB federated data sources",
            inputSchema=ExecuteSQLQueryInput.model_json_schema(),
        ),
        Tool(
            name="list_databases",
            description="List all available databases and data sources in MindsDB",
            inputSchema=ListDatabasesInput.model_json_schema(),
        ),
        Tool(
            name="describe_table",
            description="Describe table schema and metadata",
            inputSchema=DescribeTableInput.model_json_schema(),
        ),
        Tool(
            name="get_table_sample",
            description="Get sample data from a table",
            inputSchema=GetTableSampleInput.model_json_schema(),
        ),
        Tool(
            name="create_ml_model",
            description="Create a new machine learning model for training",
            inputSchema=CreateMLModelInput.model_json_schema(),
        ),
        Tool(
            name="make_prediction",
            description="Make prediction using a trained model",
            inputSchema=MakePredictionInput.model_json_schema(),
        ),
        Tool(
            name="get_model_status",
            description="Get model training status and information",
            inputSchema=GetModelStatusInput.model_json_schema(),
        ),
        Tool(
            name="evaluate_model",
            description="Evaluate model performance with metrics",
            inputSchema=EvaluateModelInput.model_json_schema(),
        ),
        Tool(
            name="forecast_time_series",
            description="Generate time series forecast using trained model",
            inputSchema=ForecastTimeSeriesInput.model_json_schema(),
        ),
    ]
