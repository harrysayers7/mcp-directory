"""
Template MCP Server

A template for creating new MCP servers. Replace this with your actual service implementation.

To create a new server:
1. Copy this template to servers/your-service-name/
2. Update pyproject.toml with your service details
3. Replace this file with your service implementation
4. Add your specific tools, resources, and prompts
5. Update README.md with service documentation
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the libs directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "libs"))

from fastmcp import FastMCP, Context

from mcp_common import (
    get_config,
    get_logger,
    setup_logging,
    MCPError,
    ValidationError,
    ExternalServiceError,
)
from mcp_common.models import (
    ToolRequest,
    ToolResponse,
    ResourceInfo,
    PromptRequest,
    PromptResponse,
)

# Initialize configuration and logging
config = get_config()
setup_logging(config.log_level)
logger = get_logger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Template MCP Server")


@mcp.tool
async def hello_world(
    name: str = "World",
    ctx: Context | None = None,
) -> dict:
    """Say hello to someone.
    
    Args:
        name: Name to greet (default: "World")
        ctx: MCP context for logging
        
    Returns:
        Dictionary containing greeting message
    """
    try:
        if ctx:
            await ctx.info(f"Greeting {name}")
        
        # Validate inputs
        if not name.strip():
            raise ValidationError("Name cannot be empty")
        
        # Tool logic
        greeting = f"Hello, {name}!"
        
        if ctx:
            await ctx.info(f"Generated greeting: {greeting}")
        
        return {
            "success": True,
            "data": {"greeting": greeting},
            "message": "Greeting generated successfully",
        }
        
    except ValidationError as e:
        raise e
    except Exception as e:
        logger.error(f"Error generating greeting: {e}")
        raise MCPError(f"Failed to generate greeting: {str(e)}")


@mcp.tool
async def get_info(
    item_id: str,
    ctx: Context | None = None,
) -> dict:
    """Get information about an item.
    
    Args:
        item_id: ID of the item to retrieve
        ctx: MCP context for logging
        
    Returns:
        Dictionary containing item information
    """
    try:
        if ctx:
            await ctx.info(f"Retrieving info for item: {item_id}")
        
        # Validate inputs
        if not item_id.strip():
            raise ValidationError("Item ID cannot be empty")
        
        # Tool logic - replace with your actual implementation
        item_info = {
            "id": item_id,
            "name": f"Item {item_id}",
            "description": "This is a template item",
            "created_at": "2024-01-01T00:00:00Z",
            "status": "active",
        }
        
        if ctx:
            await ctx.info(f"Retrieved info for item: {item_id}")
        
        return {
            "success": True,
            "data": item_info,
            "message": "Item information retrieved successfully",
        }
        
    except ValidationError as e:
        raise e
    except Exception as e:
        logger.error(f"Error retrieving item info: {e}")
        raise MCPError(f"Failed to retrieve item info: {str(e)}")


@mcp.resource
async def template_resource(uri: str, ctx: Context | None = None) -> str:
    """Access template resources.
    
    Args:
        uri: Resource URI (e.g., 'template://item/123')
        ctx: MCP context for logging
        
    Returns:
        Resource content as string
    """
    try:
        if ctx:
            await ctx.info(f"Accessing resource: {uri}")
        
        # Parse URI
        if not uri.startswith("template://"):
            raise ValidationError("Invalid URI format. Expected 'template://type/id'")
        
        parts = uri.split("/")
        if len(parts) < 3:
            raise ValidationError("Invalid URI format. Expected 'template://type/id'")
        
        resource_type = parts[2]
        resource_id = parts[3] if len(parts) > 3 else ""
        
        if not resource_id:
            raise ValidationError("Resource ID is required")
        
        # Resource logic - replace with your actual implementation
        content = f"""# {resource_type.title()} Resource

**ID**: {resource_id}
**Type**: {resource_type}
**Status**: Active

This is a template resource. Replace this with your actual resource content.

## Example Content

- Item ID: {resource_id}
- Resource Type: {resource_type}
- Created: 2024-01-01
- Last Modified: 2024-01-01

## Usage

This resource can be accessed via the MCP protocol using the URI: `{uri}`
"""
        
        if ctx:
            await ctx.info(f"Resource accessed successfully: {resource_type}/{resource_id}")
        
        return content
        
    except ValidationError as e:
        raise e
    except Exception as e:
        logger.error(f"Error accessing resource: {e}")
        raise MCPError(f"Failed to access resource: {str(e)}")


@mcp.prompt
async def template_help(ctx: Context | None = None) -> str:
    """Get help information about the template MCP server.
    
    Args:
        ctx: MCP context for logging
        
    Returns:
        Help text
    """
    return """
# Template MCP Server Help

This is a template MCP server. Replace this with your actual service documentation.

## Available Tools

### hello_world(name="World")
Say hello to someone.

### get_info(item_id)
Get information about an item.

## Available Resources

### template://item/<item_id>
Access an item resource.

## Configuration

Set the following environment variables:
- TEMPLATE_API_KEY: Your service API key (replace with actual config)

## Examples

1. Say hello:
   ```
   hello_world("Alice")
   ```

2. Get item info:
   ```
   get_info("123")
   ```

3. Access resource:
   ```
   template://item/123
   ```

## Development

To create a new MCP server from this template:

1. Copy this template to `servers/your-service-name/`
2. Update `pyproject.toml` with your service details
3. Replace this file with your service implementation
4. Add your specific tools, resources, and prompts
5. Update README.md with service documentation
6. Add tests in the `tests/` directory
"""


def main() -> None:
    """Main entry point for the template MCP server."""
    try:
        logger.info("Starting Template MCP Server")
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Shutting down Template MCP Server")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
