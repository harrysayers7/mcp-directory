"""MindsDB MCP Server - AI-powered data analytics through Model Context Protocol."""

__version__ = "0.1.0"
__author__ = "MCP Directory Team"
__email__ = "team@mcp-directory.dev"

from .main import main
from .client import MindsDBClient
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
)

__all__ = [
    "main",
    "MindsDBClient",
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
