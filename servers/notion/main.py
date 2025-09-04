"""
Notion MCP Server

A FastMCP server that provides tools, resources, and prompts for interacting
with the Notion API for document and database management.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the libs directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "libs"))

from fastmcp import FastMCP, Context
from notion_client import Client as NotionClient
from notion_client.errors import APIResponseError

from mcp_common import (
    get_config,
    get_logger,
    setup_logging,
    MCPError,
    ValidationError,
    ExternalServiceError,
    NotFoundError,
)
from mcp_common.models import (
    PaginationParams,
    PaginatedResponse,
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
mcp = FastMCP("Notion MCP Server")

# Initialize Notion client
notion_client: NotionClient | None = None


def get_notion_client() -> NotionClient:
    """Get or create Notion client."""
    global notion_client
    if notion_client is None:
        api_key = os.getenv("NOTION_API_KEY")
        if not api_key:
            raise MCPError("Notion API key not configured", "CONFIGURATION_ERROR")
        notion_client = NotionClient(auth=api_key)
    return notion_client


@mcp.tool
async def search_pages(
    query: str,
    page_size: int = 20,
    page: int = 1,
    ctx: Context | None = None,
) -> dict:
    """Search for pages in Notion.
    
    Args:
        query: Search query
        page_size: Number of results per page (1-100)
        page: Page number (1-based)
        ctx: MCP context
        
    Returns:
        Dictionary containing search results
    """
    try:
        if ctx:
            await ctx.info(f"Searching Notion pages with query: {query}")
        
        # Validate inputs
        if not query.strip():
            raise ValidationError("Query cannot be empty")
        
        if page_size < 1 or page_size > 100:
            raise ValidationError("Page size must be between 1 and 100")
        
        if page < 1:
            raise ValidationError("Page must be 1 or greater")
        
        # Get Notion client
        client = get_notion_client()
        
        # Search pages
        response = client.search(
            query=query,
            page_size=page_size,
            start_cursor=None if page == 1 else None,  # TODO: Implement pagination
        )
        
        # Process results
        results = []
        for item in response.get("results", []):
            if item["object"] == "page":
                results.append({
                    "id": item["id"],
                    "title": _extract_page_title(item),
                    "url": item.get("url", ""),
                    "created_time": item["created_time"],
                    "last_edited_time": item["last_edited_time"],
                    "properties": item.get("properties", {}),
                })
        
        # Create paginated response
        pagination = PaginationParams(page=page, page_size=page_size)
        paginated_response = PaginatedResponse(
            items=results,
            total=response.get("has_more", False) and len(results) == page_size,
            page=page,
            page_size=page_size,
        )
        
        if ctx:
            await ctx.info(f"Found {len(results)} pages")
        
        return {
            "success": True,
            "data": paginated_response.dict(),
            "message": f"Found {len(results)} pages",
        }
        
    except APIResponseError as e:
        logger.error(f"Notion API error: {e}")
        raise ExternalServiceError(
            f"Notion API error: {e.message}",
            service="notion",
            status_code=e.code,
        )
    except Exception as e:
        logger.error(f"Error searching pages: {e}")
        raise MCPError(f"Failed to search pages: {str(e)}")


@mcp.tool
async def create_page(
    parent_id: str,
    title: str,
    content: str | None = None,
    properties: dict | None = None,
    ctx: Context | None = None,
) -> dict:
    """Create a new page in Notion.
    
    Args:
        parent_id: ID of the parent page or database
        title: Page title
        content: Page content (markdown)
        properties: Additional page properties
        ctx: MCP context
        
    Returns:
        Dictionary containing the created page information
    """
    try:
        if ctx:
            await ctx.info(f"Creating Notion page: {title}")
        
        # Validate inputs
        if not parent_id.strip():
            raise ValidationError("Parent ID cannot be empty")
        
        if not title.strip():
            raise ValidationError("Title cannot be empty")
        
        # Get Notion client
        client = get_notion_client()
        
        # Prepare page data
        page_data = {
            "parent": {"page_id": parent_id},
            "properties": {
                "title": {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                }
            }
        }
        
        # Add content if provided
        if content:
            page_data["children"] = [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": content
                                }
                            }
                        ]
                    }
                }
            ]
        
        # Add additional properties
        if properties:
            page_data["properties"].update(properties)
        
        # Create page
        response = client.pages.create(**page_data)
        
        if ctx:
            await ctx.info(f"Created page with ID: {response['id']}")
        
        return {
            "success": True,
            "data": {
                "id": response["id"],
                "title": title,
                "url": response.get("url", ""),
                "created_time": response["created_time"],
                "last_edited_time": response["last_edited_time"],
            },
            "message": "Page created successfully",
        }
        
    except APIResponseError as e:
        logger.error(f"Notion API error: {e}")
        raise ExternalServiceError(
            f"Notion API error: {e.message}",
            service="notion",
            status_code=e.code,
        )
    except Exception as e:
        logger.error(f"Error creating page: {e}")
        raise MCPError(f"Failed to create page: {str(e)}")


@mcp.tool
async def get_page(page_id: str, ctx: Context | None = None) -> dict:
    """Get a specific page from Notion.
    
    Args:
        page_id: ID of the page to retrieve
        ctx: MCP context
        
    Returns:
        Dictionary containing the page information
    """
    try:
        if ctx:
            await ctx.info(f"Retrieving Notion page: {page_id}")
        
        # Validate inputs
        if not page_id.strip():
            raise ValidationError("Page ID cannot be empty")
        
        # Get Notion client
        client = get_notion_client()
        
        # Get page
        response = client.pages.retrieve(page_id=page_id)
        
        if ctx:
            await ctx.info(f"Retrieved page: {_extract_page_title(response)}")
        
        return {
            "success": True,
            "data": {
                "id": response["id"],
                "title": _extract_page_title(response),
                "url": response.get("url", ""),
                "created_time": response["created_time"],
                "last_edited_time": response["last_edited_time"],
                "properties": response.get("properties", {}),
                "parent": response.get("parent", {}),
            },
            "message": "Page retrieved successfully",
        }
        
    except APIResponseError as e:
        if e.code == 404:
            raise NotFoundError("Page not found", resource_type="page", resource_id=page_id)
        logger.error(f"Notion API error: {e}")
        raise ExternalServiceError(
            f"Notion API error: {e.message}",
            service="notion",
            status_code=e.code,
        )
    except Exception as e:
        logger.error(f"Error retrieving page: {e}")
        raise MCPError(f"Failed to retrieve page: {str(e)}")


@mcp.tool
async def update_page(
    page_id: str,
    properties: dict | None = None,
    content: str | None = None,
    ctx: Context | None = None,
) -> dict:
    """Update a page in Notion.
    
    Args:
        page_id: ID of the page to update
        properties: Properties to update
        content: New content (markdown)
        ctx: MCP context
        
    Returns:
        Dictionary containing the updated page information
    """
    try:
        if ctx:
            await ctx.info(f"Updating Notion page: {page_id}")
        
        # Validate inputs
        if not page_id.strip():
            raise ValidationError("Page ID cannot be empty")
        
        # Get Notion client
        client = get_notion_client()
        
        # Prepare update data
        update_data = {}
        
        if properties:
            update_data["properties"] = properties
        
        # Update page
        response = client.pages.update(page_id=page_id, **update_data)
        
        # Update content if provided
        if content:
            # First, get existing blocks
            blocks_response = client.blocks.children.list(block_id=page_id)
            
            # Delete existing blocks
            for block in blocks_response.get("results", []):
                client.blocks.delete(block_id=block["id"])
            
            # Add new content
            client.blocks.children.append(
                block_id=page_id,
                children=[
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": content
                                    }
                                }
                            ]
                        }
                    }
                ]
            )
        
        if ctx:
            await ctx.info(f"Updated page: {_extract_page_title(response)}")
        
        return {
            "success": True,
            "data": {
                "id": response["id"],
                "title": _extract_page_title(response),
                "url": response.get("url", ""),
                "last_edited_time": response["last_edited_time"],
            },
            "message": "Page updated successfully",
        }
        
    except APIResponseError as e:
        if e.code == 404:
            raise NotFoundError("Page not found", resource_type="page", resource_id=page_id)
        logger.error(f"Notion API error: {e}")
        raise ExternalServiceError(
            f"Notion API error: {e.message}",
            service="notion",
            status_code=e.code,
        )
    except Exception as e:
        logger.error(f"Error updating page: {e}")
        raise MCPError(f"Failed to update page: {str(e)}")


@mcp.tool
async def get_database(database_id: str, ctx: Context | None = None) -> dict:
    """Get a database from Notion.
    
    Args:
        database_id: ID of the database to retrieve
        ctx: MCP context
        
    Returns:
        Dictionary containing the database information
    """
    try:
        if ctx:
            await ctx.info(f"Retrieving Notion database: {database_id}")
        
        # Validate inputs
        if not database_id.strip():
            raise ValidationError("Database ID cannot be empty")
        
        # Get Notion client
        client = get_notion_client()
        
        # Get database
        response = client.databases.retrieve(database_id=database_id)
        
        if ctx:
            await ctx.info(f"Retrieved database: {response.get('title', [{}])[0].get('plain_text', 'Untitled')}")
        
        return {
            "success": True,
            "data": {
                "id": response["id"],
                "title": response.get("title", [{}])[0].get("plain_text", "Untitled"),
                "url": response.get("url", ""),
                "created_time": response["created_time"],
                "last_edited_time": response["last_edited_time"],
                "properties": response.get("properties", {}),
                "parent": response.get("parent", {}),
            },
            "message": "Database retrieved successfully",
        }
        
    except APIResponseError as e:
        if e.code == 404:
            raise NotFoundError("Database not found", resource_type="database", resource_id=database_id)
        logger.error(f"Notion API error: {e}")
        raise ExternalServiceError(
            f"Notion API error: {e.message}",
            service="notion",
            status_code=e.code,
        )
    except Exception as e:
        logger.error(f"Error retrieving database: {e}")
        raise MCPError(f"Failed to retrieve database: {str(e)}")


@mcp.resource("notion://{type}/{id}")
async def notion_pages(type: str, id: str, ctx: Context | None = None) -> str:
    """Access Notion pages as resources.
    
    Args:
        type: Resource type ('page' or 'database')
        id: Resource ID
        ctx: MCP context
        
    Returns:
        Resource content as JSON string
    """
    try:
        if ctx:
            await ctx.info(f"Accessing Notion resource: {type}/{id}")
        
        # Validate resource type
        if type not in ["page", "database"]:
            raise ValidationError(f"Unsupported resource type: {type}")
        
        if not id:
            raise ValidationError("Resource ID is required")
        
        # Get Notion client
        client = get_notion_client()
        
        if type == "page":
            # Get page content
            page = client.pages.retrieve(page_id=id)
            blocks = client.blocks.children.list(block_id=id)
            
            content = f"# {_extract_page_title(page)}\n\n"
            for block in blocks.get("results", []):
                content += _extract_block_content(block) + "\n"
            
            return content
            
        elif type == "database":
            # Get database content
            database = client.databases.retrieve(database_id=id)
            pages = client.databases.query(database_id=id)
            
            content = f"# {database.get('title', [{}])[0].get('plain_text', 'Untitled Database')}\n\n"
            for page in pages.get("results", []):
                content += f"## {_extract_page_title(page)}\n\n"
                for prop_name, prop_value in page.get("properties", {}).items():
                    content += f"**{prop_name}**: {_extract_property_value(prop_value)}\n"
                content += "\n"
            
            return content
            
        else:
            raise ValidationError(f"Unsupported resource type: {type}")
        
    except APIResponseError as e:
        if e.code == 404:
            raise NotFoundError("Resource not found", resource_type=type, resource_id=id)
        logger.error(f"Notion API error: {e}")
        raise ExternalServiceError(
            f"Notion API error: {e.message}",
            service="notion",
            status_code=e.code,
        )
    except Exception as e:
        logger.error(f"Error accessing resource: {e}")
        raise MCPError(f"Failed to access resource: {str(e)}")


@mcp.prompt
async def notion_help(ctx: Context | None = None) -> str:
    """Get help information about Notion MCP server.
    
    Args:
        ctx: MCP context
        
    Returns:
        Help text
    """
    return """
# Notion MCP Server Help

This server provides tools for interacting with Notion pages and databases.

## Available Tools

### search_pages(query, page_size=20, page=1)
Search for pages in Notion using a query string.

### create_page(parent_id, title, content=None, properties=None)
Create a new page in Notion.

### get_page(page_id)
Retrieve a specific page by its ID.

### update_page(page_id, properties=None, content=None)
Update an existing page's properties or content.

### get_database(database_id)
Retrieve a specific database by its ID.

## Available Resources

### notion://page/<page_id>
Access a Notion page as a resource.

### notion://database/<database_id>
Access a Notion database as a resource.

## Configuration

Set the following environment variables:
- NOTION_API_KEY: Your Notion integration API key

## Examples

1. Search for pages:
   ```
   search_pages("project planning")
   ```

2. Create a new page:
   ```
   create_page("parent-page-id", "New Page Title", "Page content here")
   ```

3. Access a page as a resource:
   ```
   notion://page/12345678-1234-1234-1234-123456789012
   ```
"""


def _extract_page_title(page: dict) -> str:
    """Extract title from a Notion page."""
    properties = page.get("properties", {})
    for prop_name, prop_value in properties.items():
        if prop_value.get("type") == "title":
            title_array = prop_value.get("title", [])
            if title_array:
                return title_array[0].get("plain_text", "Untitled")
    return "Untitled"


def _extract_block_content(block: dict) -> str:
    """Extract content from a Notion block."""
    block_type = block.get("type", "")
    
    if block_type == "paragraph":
        rich_text = block.get("paragraph", {}).get("rich_text", [])
        return "".join([text.get("plain_text", "") for text in rich_text])
    
    elif block_type == "heading_1":
        rich_text = block.get("heading_1", {}).get("rich_text", [])
        content = "".join([text.get("plain_text", "") for text in rich_text])
        return f"# {content}"
    
    elif block_type == "heading_2":
        rich_text = block.get("heading_2", {}).get("rich_text", [])
        content = "".join([text.get("plain_text", "") for text in rich_text])
        return f"## {content}"
    
    elif block_type == "heading_3":
        rich_text = block.get("heading_3", {}).get("rich_text", [])
        content = "".join([text.get("plain_text", "") for text in rich_text])
        return f"### {content}"
    
    elif block_type == "bulleted_list_item":
        rich_text = block.get("bulleted_list_item", {}).get("rich_text", [])
        content = "".join([text.get("plain_text", "") for text in rich_text])
        return f"- {content}"
    
    elif block_type == "numbered_list_item":
        rich_text = block.get("numbered_list_item", {}).get("rich_text", [])
        content = "".join([text.get("plain_text", "") for text in rich_text])
        return f"1. {content}"
    
    else:
        return ""


def _extract_property_value(property_value: dict) -> str:
    """Extract value from a Notion property."""
    prop_type = property_value.get("type", "")
    
    if prop_type == "title":
        title_array = property_value.get("title", [])
        return "".join([text.get("plain_text", "") for text in title_array])
    
    elif prop_type == "rich_text":
        rich_text_array = property_value.get("rich_text", [])
        return "".join([text.get("plain_text", "") for text in rich_text_array])
    
    elif prop_type == "select":
        select_value = property_value.get("select")
        return select_value.get("name", "") if select_value else ""
    
    elif prop_type == "multi_select":
        multi_select_array = property_value.get("multi_select", [])
        return ", ".join([option.get("name", "") for option in multi_select_array])
    
    elif prop_type == "date":
        date_value = property_value.get("date")
        return date_value.get("start", "") if date_value else ""
    
    elif prop_type == "checkbox":
        return "Yes" if property_value.get("checkbox") else "No"
    
    elif prop_type == "number":
        return str(property_value.get("number", ""))
    
    else:
        return str(property_value)


def main() -> None:
    """Main entry point for the Notion MCP server."""
    try:
        logger.info("Starting Notion MCP Server")
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Shutting down Notion MCP Server")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
