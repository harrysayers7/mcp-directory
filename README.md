# MCP Servers Monorepo

A comprehensive monorepo of Model Context Protocol (MCP) servers built with FastMCP, designed for enterprise-grade deployment with security, scalability, and maintainability as core principles.

## 🏗️ Architecture

```
mcp-directory/
├── servers/                    # Individual MCP servers
│   ├── notion/                # Notion MCP server
│   ├── github/                # GitHub MCP server
│   ├── supabase/              # Supabase MCP server
│   └── template/              # Server template for new servers
├── libs/                      # Shared libraries
│   └── mcp_common/           # Common utilities and patterns
├── docs/                      # Documentation
│   ├── ai/                    # AI assistant documentation
│   └── api/                   # API documentation
├── .cursor/                   # Cursor IDE rules
│   └── rules/                 # MDC rule files
├── .github/                   # GitHub Actions workflows
│   └── workflows/
├── docker/                    # Docker configurations
│   ├── docker-compose.yml     # Local development orchestration
│   └── base/                  # Base Docker images
└── scripts/                   # Development and deployment scripts
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- UV package manager (recommended)
- Git

### Development Setup

1. **Clone and setup the repository:**
   ```bash
   git clone <repository-url>
   cd mcp-directory
   uv sync
   ```

2. **Start local development environment:**
   ```bash
   docker-compose up -d
   ```

3. **Run a specific server:**
   ```bash
   cd servers/notion
   uv run python main.py
   ```

## 📦 Available Servers

### Notion MCP Server
- **Purpose**: Notion API integration for document and database management
- **Features**: Search, create, update, and manage Notion pages and databases
- **Tools**: `search_pages`, `create_page`, `update_page`, `get_database`
- **Resources**: Notion pages and databases
- **Prompts**: Notion-specific AI prompts

### GitHub MCP Server
- **Purpose**: GitHub API integration for repository management
- **Features**: Repository operations, issue management, pull request handling
- **Tools**: `get_repo`, `create_issue`, `list_pull_requests`, `search_code`
- **Resources**: GitHub repositories and issues
- **Prompts**: GitHub-specific AI prompts

### Supabase MCP Server
- **Purpose**: Supabase integration for database and authentication
- **Features**: Database operations, user management, real-time subscriptions
- **Tools**: `query_database`, `create_user`, `subscribe_to_changes`
- **Resources**: Supabase tables and functions
- **Prompts**: Supabase-specific AI prompts

## 🛠️ Development

### Adding a New Server

1. **Use the template:**
   ```bash
   cp -r servers/template servers/my-new-server
   cd servers/my-new-server
   ```

2. **Update configuration:**
   - Modify `pyproject.toml` with your server details
   - Update `main.py` with your tools and resources
   - Add your specific environment variables

3. **Implement your tools:**
   ```python
   from fastmcp import FastMCP
   from mcp_common import BaseMCPTool
   
   mcp = FastMCP("My New Server")
   
   @mcp.tool
   async def my_tool(param: str) -> str:
       return f"Hello from {param}!"
   ```

### Shared Library Usage

The `libs/mcp_common` package provides:

- **BaseMCPTool**: Base class for MCP tools with common patterns
- **Authentication**: OAuth and API key management
- **Logging**: Structured logging with correlation IDs
- **Error Handling**: Standardized error responses
- **Configuration**: Environment-based configuration management
- **Validation**: Pydantic models for request/response validation

## 🔒 Security

This monorepo implements enterprise-grade security practices:

- **OWASP Top 10** compliance
- **ASD Essential Eight** implementation
- **ISO 27001** security controls
- **No secrets in code** (environment variables + vault integration)
- **Automated security scanning** (trufflehog, semgrep)
- **Pre-commit hooks** for code quality and security

### Security Tools

- **Ruff**: Python linting and formatting
- **MyPy**: Type checking
- **TruffleHog**: Secret scanning
- **Semgrep**: Static analysis
- **Bandit**: Security linting
- **Safety**: Dependency vulnerability scanning

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run tests for specific server
pytest servers/notion/

# Run with coverage
pytest --cov=servers --cov=libs --cov-report=html
```

### Test Structure

```
servers/notion/
├── tests/
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── fixtures/              # Test fixtures
└── conftest.py               # Pytest configuration
```

## 🚀 Deployment

### Docker Deployment

Each server has its own Dockerfile and can be deployed independently:

```bash
# Build specific server
docker build -t mcp-notion servers/notion/

# Run with docker-compose
docker-compose up notion
```

### CI/CD Pipeline

GitHub Actions automatically:

- **Tests**: Run unit and integration tests
- **Security**: Scan for vulnerabilities and secrets
- **Build**: Create Docker images
- **Deploy**: Deploy to staging/production environments

## 📚 Documentation

### AI Assistant Integration

This monorepo includes comprehensive AI assistant integration:

- **`.cursor/rules/`**: Cursor IDE rules for context-aware development
- **`docs/ai/`**: AI-specific documentation and diagrams
- **Mermaid diagrams**: Architecture and flow diagrams
- **API documentation**: OpenAPI specifications

### Documentation Structure

```
docs/
├── ai/                       # AI assistant documentation
│   ├── architecture.md      # System architecture
│   ├── development.md       # Development guidelines
│   └── deployment.md        # Deployment guide
├── api/                     # API documentation
│   ├── notion/             # Notion API docs
│   ├── github/             # GitHub API docs
│   └── supabase/           # Supabase API docs
└── diagrams/               # Mermaid diagrams
    ├── architecture.mmd    # System architecture
    └── deployment.mmd      # Deployment flow
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/my-feature`
3. **Make your changes** following the coding standards
4. **Run tests and linting**: `pre-commit run --all-files`
5. **Commit your changes**: `git commit -m "Add my feature"`
6. **Push to the branch**: `git push origin feature/my-feature`
7. **Open a Pull Request**

### Development Standards

- **Python 3.11+** with type hints
- **FastMCP** framework for all servers
- **Pytest** for comprehensive testing
- **Ruff** for linting and formatting
- **MyPy** for type checking
- **Pre-commit hooks** for automated quality checks

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the `docs/` directory
- **Issues**: Open an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions
- **AI Assistant**: Use Cursor with the provided rules for development guidance

## 🗺️ Roadmap

- [ ] Additional MCP servers (Slack, Discord, Jira)
- [ ] Advanced monitoring and observability
- [ ] Multi-cloud deployment support
- [ ] Enterprise SSO integration
- [ ] Performance optimization and caching
- [ ] Advanced security features
