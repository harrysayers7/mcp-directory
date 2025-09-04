# MindsDB MCP Server Makefile

.PHONY: help install dev-install test lint format typecheck clean run docker-build docker-run docker-compose-up docker-compose-down

# Default target
help:
	@echo "Available commands:"
	@echo "  install        Install production dependencies"
	@echo "  dev-install    Install development dependencies"
	@echo "  test           Run tests"
	@echo "  test-unit      Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  lint           Run linting checks"
	@echo "  format         Format code"
	@echo "  typecheck      Run type checking"
	@echo "  clean          Clean build artifacts"
	@echo "  run            Run the server"
	@echo "  docker-build   Build Docker image"
	@echo "  docker-run     Run Docker container"
	@echo "  docker-compose-up   Start services with Docker Compose"
	@echo "  docker-compose-down Stop services with Docker Compose"

# Installation
install:
	pip install -e .

dev-install:
	pip install -e ".[dev]"
	pre-commit install

# Testing
test: test-unit test-integration

test-unit:
	pytest tests/ -v --cov=src/mindsdb_mcp_server --cov-report=html --cov-report=term

test-integration:
	pytest tests/integration/ -v -m integration

test-coverage:
	pytest tests/ --cov=src/mindsdb_mcp_server --cov-report=html --cov-report=xml

# Code quality
lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

format:
	ruff format src/ tests/
	ruff check --fix src/ tests/

typecheck:
	mypy src/

# Cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run server
run:
	python -m mindsdb_mcp_server.main

# Docker commands
docker-build:
	docker build -t mindsdb-mcp-server .

docker-run:
	docker run --rm -p 8000:8000 \
		-e MINDSDB_API_KEY=$${MINDSDB_API_KEY} \
		-e REDIS_HOST=host.docker.internal \
		mindsdb-mcp-server

docker-compose-up:
	docker-compose up -d

docker-compose-down:
	docker-compose down

docker-compose-logs:
	docker-compose logs -f

# Development helpers
dev-setup: dev-install
	@echo "Setting up development environment..."
	@echo "Make sure to set environment variables:"
	@echo "  export MINDSDB_API_KEY=your-api-key"
	@echo "  export REDIS_HOST=localhost"
	@echo "  export REDIS_PORT=6379"

# Pre-commit hooks
pre-commit:
	pre-commit run --all-files

# Security checks
security:
	bandit -r src/
	safety check

# Performance testing
perf-test:
	pytest tests/ -m "not slow" --benchmark-only

# Documentation
docs:
	@echo "Generating documentation..."
	@echo "See README.md for usage instructions"

# Release helpers
version:
	@python -c "import mindsdb_mcp_server; print(mindsdb_mcp_server.__version__)"

# Environment setup
env-example:
	@echo "Copying environment example..."
	cp env.example .env
	@echo "Edit .env with your configuration"

# All-in-one development setup
setup: dev-setup env-example
	@echo "Development environment setup complete!"
	@echo "Next steps:"
	@echo "1. Edit .env with your configuration"
	@echo "2. Run 'make test' to verify everything works"
	@echo "3. Run 'make run' to start the server"
