# FastAPI Question Service

A structured FastAPI application with a question-answering API endpoint.

## Features

- **Structured Architecture**: Well-organized code with separate modules for models, services, routers, and configuration
- **RESTful API**: Clean API design with proper request/response models
- **Header-based Authentication**: Uses `user-name` and `employee-id` headers for user identification
- **Comprehensive Documentation**: Auto-generated API docs with Swagger UI
- **Error Handling**: Proper HTTP status codes and error responses
- **Logging**: Structured logging for debugging and monitoring
- **Modern Package Management**: Uses `uv` for fast dependency management

## Prerequisites

- Python 3.8 or higher
- `uv` package manager (install with `curl -LsSf https://astral.sh/uv/install.sh | sh`)

## Project Structure

```
redis_caching_session/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── __main__.py          # Application entry point
│   ├── config.py            # Configuration settings
│   ├── models.py            # Pydantic models for requests/responses
│   ├── routers.py           # API route definitions
│   └── services.py          # Business logic
├── main.py                  # Main entry point
├── pyproject.toml           # Project configuration and dependencies
├── uv.lock                  # Locked dependency versions
├── Makefile                 # Development tasks
├── .gitignore              # Git ignore patterns
└── README.md               # This file
```

## Quick Start

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Run the application**:
   ```bash
   uv run python main.py
   ```
   
   Or use the Makefile:
   ```bash
   make run
   ```

3. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/api/v1/health

## Development

### Setup Development Environment

```bash
# Install development dependencies
uv sync --dev

# Or use Makefile
make install-dev
```

### Available Commands

```bash
# Show all available commands
make help

# Install dependencies
make install          # Production dependencies
make install-dev      # Development dependencies

# Run the application
make run              # Run with main.py
make run-dev          # Run with module mode

# Testing
make test             # Run tests
make test-watch       # Run tests in watch mode

# Code Quality
make lint             # Run linting (flake8, mypy)
make format           # Format code (black, isort)
make format-check     # Check formatting without changes
make check            # Run all checks (format, lint, test)

# Cleanup
make clean            # Remove generated files
```

### Using uv Commands Directly

```bash
# Install dependencies
uv sync               # Install all dependencies
uv sync --dev         # Install with development dependencies

# Run commands
uv run python main.py
uv run pytest
uv run black app/
uv run mypy app/

# Add new dependencies
uv add package-name
uv add --dev package-name  # Development dependency
```

## API Endpoints

### POST /api/v1/ask

Submit a question and receive a response.

**Headers Required**:
- `user-name`: The name of the user
- `employee-id`: The employee ID of the user

**Request Body**:
```json
{
  "question": "What is your name?"
}
```

**Response**:
```json
{
  "user_name": "John Doe",
  "employee_id": "EMP123",
  "question": "What is your name?",
  "response": "My name is AI Assistant. Nice to meet you, John Doe!",
  "status": "success"
}
```

### GET /api/v1/health

Health check endpoint to verify the API is running.

**Response**:
```json
{
  "status": "healthy",
  "message": "API is running successfully"
}
```

## Example Usage

### Using curl:

```bash
curl -X POST "http://localhost:8000/api/v1/ask" \
  -H "user-name: John Doe" \
  -H "employee-id: EMP123" \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello, how are you?"}'
```

### Using Python requests:

```python
import requests

url = "http://localhost:8000/api/v1/ask"
headers = {
    "user-name": "John Doe",
    "employee-id": "EMP123",
    "Content-Type": "application/json"
}
data = {"question": "Hello, how are you?"}

response = requests.post(url, headers=headers, json=data)
print(response.json())
```

## Configuration

The application uses `pydantic-settings` for configuration management. You can:

1. Set environment variables
2. Create a `.env` file
3. Modify the default values in `app/config.py`

## Testing

The project includes a comprehensive test setup with pytest:

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=app

# Run specific test file
uv run pytest tests/test_routers.py

# Run tests in watch mode
uv run pytest --watch
```

## Code Quality

The project uses several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

Run all quality checks:
```bash
make check
```

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Successful response
- `400`: Bad request (missing or invalid headers)
- `422`: Validation error (invalid request body)

## Logging

The application includes structured logging. Logs are output to the console with timestamps and log levels.

## Why uv?

`uv` is a fast Python package installer and resolver written in Rust. It offers:

- **Speed**: Much faster than pip and other package managers
- **Reliability**: Better dependency resolution
- **Compatibility**: Works with existing Python projects
- **Modern**: Uses `pyproject.toml` for configuration
- **Lock files**: Ensures reproducible builds with `uv.lock`
