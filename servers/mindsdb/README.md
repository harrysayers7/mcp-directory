# MindsDB MCP Server

A Model Context Protocol (MCP) server that provides AI-powered data analytics capabilities through MindsDB. This server enables AI assistants to interact with MindsDB's federated data sources and machine learning capabilities.

## Features

- **SQL Query Execution**: Execute SQL queries against any data source connected to MindsDB
- **Database Management**: List databases, describe tables, and get sample data
- **Machine Learning**: Create, train, and evaluate ML models with AutoML capabilities
- **Predictions**: Make predictions using trained models with confidence scores
- **Time Series Forecasting**: Generate forecasts for time series data
- **Caching**: Redis-based caching for improved performance
- **Security**: Role-based access control and secure credential management

## Quick Start

### Prerequisites

- Python 3.11+
- Redis (for caching)
- MindsDB API key or local MindsDB instance

### Installation

1. **Clone and install**:
   ```bash
   git clone <repository-url>
   cd servers/mindsdb
   pip install -e .
   ```

2. **Set environment variables**:
   ```bash
   export MINDSDB_API_KEY="your-api-key"
   export MINDSDB_HOST="https://cloud.mindsdb.com"  # or local instance
   export REDIS_HOST="localhost"
   export REDIS_PORT="6379"
   ```

3. **Run the server**:
   ```bash
   python -m mindsdb_mcp_server.main
   ```

### Docker Deployment

1. **Using Docker Compose**:
   ```bash
   # Copy environment file
   cp .env.example .env
   # Edit .env with your configuration
   
   # Start services
   docker-compose up -d
   ```

2. **Using Docker**:
   ```bash
   docker build -t mindsdb-mcp-server .
   docker run -e MINDSDB_API_KEY="your-key" mindsdb-mcp-server
   ```

## Configuration

The server can be configured using environment variables or a `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `MINDSDB_API_KEY` | - | MindsDB API key for authentication |
| `MINDSDB_HOST` | `https://cloud.mindsdb.com` | MindsDB host URL |
| `MINDSDB_PORT` | `47334` | MindsDB port |
| `REDIS_HOST` | `localhost` | Redis host for caching |
| `REDIS_PORT` | `6379` | Redis port |
| `REDIS_PASSWORD` | - | Redis password |
| `LOG_LEVEL` | `INFO` | Logging level |
| `LOG_FORMAT` | `json` | Log format (json or text) |
| `QUERY_TIMEOUT` | `300` | Query timeout in seconds |
| `CACHE_TTL` | `3600` | Cache TTL in seconds |

## Available Tools

### Data Query Tools

- **`execute_sql_query`**: Execute SQL queries against MindsDB data sources
- **`list_databases`**: List all available databases and data sources
- **`describe_table`**: Get table schema and metadata
- **`get_table_sample`**: Get sample data from tables

### Machine Learning Tools

- **`create_ml_model`**: Create and train new ML models
- **`make_prediction`**: Make predictions using trained models
- **`get_model_status`**: Get model training status and information
- **`evaluate_model`**: Evaluate model performance with metrics
- **`forecast_time_series`**: Generate time series forecasts

## Usage Examples

### Basic Data Analysis

```python
# List available databases
databases = await list_databases()

# Describe a table
schema = await describe_table("my_database", "my_table")

# Get sample data
sample = await get_table_sample("my_database", "my_table", limit=10)

# Execute SQL query
result = await execute_sql_query(
    "SELECT * FROM my_database.my_table WHERE created_at > '2024-01-01'"
)
```

### Machine Learning Workflow

```python
# Create a model
model = await create_ml_model(
    model_name="sales_forecast",
    query="SELECT * FROM sales_data",
    target_column="sales_amount",
    problem_type="regression"
)

# Check training status
status = await get_model_status("sales_forecast")

# Make predictions
predictions = await make_prediction(
    model_name="sales_forecast",
    data=[{"product_id": 123, "month": "2024-02"}]
)

# Evaluate model
metrics = await evaluate_model("sales_forecast")
```

### Time Series Forecasting

```python
# Create time series model
model = await create_ml_model(
    model_name="demand_forecast",
    query="SELECT * FROM demand_data ORDER BY date",
    target_column="demand",
    problem_type="time_series"
)

# Generate forecast
forecast = await forecast_time_series(
    model_name="demand_forecast",
    horizon=30,
    frequency="daily"
)
```

## Integration with AI Assistants

### Cursor Integration

Add to your `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "mindsdb": {
      "command": "python",
      "args": ["-m", "mindsdb_mcp_server.main"],
      "env": {
        "MINDSDB_API_KEY": "your-api-key",
        "REDIS_HOST": "localhost"
      }
    }
  }
}
```

### OpenAI Integration

```python
import openai

client = openai.OpenAI(
    api_key="your-openai-key",
    tools=[{
        "type": "mcp",
        "server_label": "mindsdb",
        "server_url": "http://localhost:8000",
        "headers": {"Authorization": "Bearer your-mindsdb-key"}
    }]
)
```

## Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run linting
black src/ tests/
isort src/ tests/
flake8 src/ tests/
mypy src/
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/mindsdb_mcp_server

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m slow
```

## Security

- **Authentication**: Uses MindsDB API keys for authentication
- **Input Validation**: All inputs are validated using Pydantic models
- **SQL Injection Prevention**: Uses parameterized queries and input sanitization
- **Rate Limiting**: Configurable rate limiting to prevent abuse
- **Caching**: Secure Redis-based caching with TTL
- **Logging**: Comprehensive logging without exposing sensitive data

## Performance

- **Connection Pooling**: Efficient connection management
- **Caching**: Redis-based caching for frequently accessed data
- **Async Operations**: Fully asynchronous for better concurrency
- **Query Optimization**: Automatic query optimization suggestions
- **Resource Monitoring**: Built-in resource usage monitoring

## Troubleshooting

### Common Issues

1. **Connection Failed**: Check MindsDB API key and host configuration
2. **Redis Connection Error**: Ensure Redis is running and accessible
3. **Query Timeout**: Increase `QUERY_TIMEOUT` for long-running queries
4. **Memory Issues**: Adjust `MAX_CONNECTIONS` and enable caching

### Debug Mode

```bash
export LOG_LEVEL=DEBUG
export LOG_FORMAT=text
python -m mindsdb_mcp_server.main
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- **Documentation**: [MCP Directory Docs](https://mcp-directory.dev)
- **Issues**: [GitHub Issues](https://github.com/mcp-directory/mindsdb-mcp-server/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mcp-directory/mindsdb-mcp-server/discussions)
