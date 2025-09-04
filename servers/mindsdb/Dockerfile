# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Copy source code
COPY src/ ./src/
COPY README.md ./

# Create non-root user
RUN useradd --create-home --shell /bin/bash mindsdb && \
    chown -R mindsdb:mindsdb /app
USER mindsdb

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import asyncio; from mindsdb_mcp_server.main import main; asyncio.run(main())" || exit 1

# Expose port (if needed for HTTP interface)
EXPOSE 8000

# Default command
CMD ["python", "-m", "mindsdb_mcp_server.main"]
