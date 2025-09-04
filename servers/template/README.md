# Template MCP Server

This is a template for creating new MCP servers in the MCP Directory monorepo.

## Purpose

Replace this with a description of what your MCP server does.

## Features

- List the main features of your server
- What tools it provides
- What resources it exposes
- What prompts it offers

## Installation

```bash
# Install dependencies
uv sync

# Run the server
uv run python main.py
```

## Configuration

Set the following environment variables:

```bash
# Required
YOUR_SERVICE_API_KEY=your-api-key-here

# Optional
YOUR_SERVICE_BASE_URL=https://api.yourservice.com
YOUR_SERVICE_TIMEOUT=30
```

## Usage

### Tools

#### tool_name(param1, param2=default)
Description of what this tool does.

**Parameters:**
- `param1` (str): Description of param1
- `param2` (int, optional): Description of param2 (default: 10)

**Returns:**
- Dictionary containing the result

**Example:**
```python
result = await tool_name("example", param2=20)
```

### Resources

#### yourservice://type/id
Access a resource from your service.

**Example:**
```
yourservice://item/123456
yourservice://user/789012
```

### Prompts

#### your_service_help()
Get help information about this MCP server.

## Development

### Running Tests

```bash
# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run all tests with coverage
pytest --cov=template_server --cov-report=html
```

### Code Quality

```bash
# Run linting
ruff check .

# Format code
ruff format .

# Type checking
mypy .
```

### Docker

```bash
# Build image
docker build -f Dockerfile -t mcp-template .

# Run container
docker run -p 8000:8000 --env-file .env mcp-template
```

## API Reference

### Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `tool_name` | Description | `param1`, `param2` |
| `another_tool` | Description | `param` |

### Resources

| URI Pattern | Description |
|-------------|-------------|
| `yourservice://item/<id>` | Item resource |
| `yourservice://user/<id>` | User resource |

## Troubleshooting

### Common Issues

1. **API Key Not Set**: Ensure `YOUR_SERVICE_API_KEY` is set
2. **Connection Timeout**: Check network connectivity and timeout settings
3. **Rate Limiting**: Implement proper rate limiting and retry logic

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python main.py
```

### Logs

View server logs:

```bash
# Local development
tail -f logs/server.log

# Docker
docker logs mcp-template
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run quality checks
6. Submit a pull request

## License

MIT License - see LICENSE file for details.
