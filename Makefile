.PHONY: help install install-dev run test lint format clean setup-redis start-redis stop-redis

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	uv sync

install-dev: ## Install development dependencies
	uv sync --dev

run: ## Run the FastAPI application
	uv run python main.py

run-dev: ## Run the FastAPI application in development mode
	uv run python -m app

test: ## Run tests
	uv run pytest

test-watch: ## Run tests in watch mode
	uv run pytest --watch

lint: ## Run linting checks
	uv run flake8 app/ tests/
	uv run mypy app/

format: ## Format code with black and isort
	uv run black app/ tests/
	uv run isort app/ tests/

format-check: ## Check if code is formatted correctly
	uv run black --check app/ tests/
	uv run isort --check-only app/ tests/

clean: ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

check: format-check lint test ## Run all checks (format, lint, test)

setup-redis: ## Set up Redis for session management
	@echo "Setting up Redis for session management..."
	python setup_redis.py

start-redis: ## Start Redis server
	@echo "Starting Redis server..."
	redis-server --daemonize yes

stop-redis: ## Stop Redis server
	@echo "Stopping Redis server..."
	redis-cli shutdown

dev-setup: install-dev setup-redis ## Set up development environment
	@echo "Development environment set up successfully!"
	@echo "Run 'make run' to start the application"
	@echo "Run 'make test' to run tests"
	@echo "Run 'make lint' to run linting"
	@echo "Run 'make format' to format code"
