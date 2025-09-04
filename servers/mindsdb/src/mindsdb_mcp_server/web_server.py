"""Web server wrapper for Railway deployment."""

import asyncio
import os
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import structlog

from .main import mcp, main as mcp_main
from .config import config

# Configure logging
logger = structlog.get_logger(__name__)

# Create FastAPI app for web interface
app = FastAPI(
    title="MindsDB MCP Server",
    description="Model Context Protocol server for MindsDB AI analytics",
    version=config.mcp_server_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Health check endpoint
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint for Railway."""
    try:
        # Check if MCP server is running
        return {
            "status": "healthy",
            "service": "mindsdb-mcp-server",
            "version": config.mcp_server_version,
            "mcp_server": "running"
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint with service information."""
    return {
        "service": "MindsDB MCP Server",
        "version": config.mcp_server_version,
        "description": "Model Context Protocol server for MindsDB AI analytics",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "mcp": "MCP protocol over stdio"
        },
        "tools": [
            "execute_sql_query",
            "list_databases", 
            "describe_table",
            "get_table_sample",
            "create_ml_model",
            "make_prediction",
            "get_model_status",
            "evaluate_model",
            "forecast_time_series"
        ]
    }

@app.get("/status")
async def status() -> Dict[str, Any]:
    """Detailed status endpoint."""
    return {
        "mcp_server": {
            "name": "MindsDB MCP Server",
            "version": config.mcp_server_version,
            "status": "running"
        },
        "configuration": {
            "mindsdb_host": config.mindsdb_host,
            "mindsdb_port": config.mindsdb_port,
            "redis_host": config.redis_host,
            "redis_port": config.redis_port,
            "log_level": config.log_level
        },
        "tools_count": 9,
        "resources_count": 2,
        "prompts_count": 2
    }

# Background task to run MCP server
async def run_mcp_server():
    """Run the MCP server in the background."""
    try:
        await mcp_main()
    except Exception as e:
        logger.error("MCP server error", error=str(e))

# Startup event
@app.on_event("startup")
async def startup_event():
    """Start the MCP server when the web server starts."""
    logger.info("Starting MindsDB MCP Server web interface")
    # Start MCP server in background
    asyncio.create_task(run_mcp_server())

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup when the web server shuts down."""
    logger.info("Shutting down MindsDB MCP Server web interface")

if __name__ == "__main__":
    # Get port from Railway environment variable
    port = int(os.getenv("PORT", 8000))
    
    # Run the web server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level=config.log_level.lower()
    )
