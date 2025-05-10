.PHONY: setup clean test run-local run-k8s help

# Variables
PYTHON := python3
VENV := venv
PIP := $(VENV)/bin/pip
PYTHON_VENV := $(VENV)/bin/python

# Default tickers for stock price job
TICKERS ?= AAPL,GOOGL,MSFT,AMZN,META

help:
	@echo "Available commands:"
	@echo "  make setup        - Create virtual environment and install dependencies"
	@echo "  make clean        - Remove virtual environment and cache files"
	@echo "  make run-local    - Run stock price job locally (default tickers: $(TICKERS))"
	@echo "  make run-k8s      - Run stock price job on Kubernetes (default tickers: $(TICKERS))"
	@echo "  make test         - Run tests"
	@echo ""
	@echo "Usage examples:"
	@echo "  make run-local TICKERS=AAPL,GOOGL"
	@echo "  make run-k8s TICKERS=MSFT,AMZN"

setup:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)
	@echo "Installing dependencies..."
	$(PIP) install -r requirements.txt
	@echo "Setup complete! Activate the virtual environment with: source $(VENV)/bin/activate"

clean:
	@echo "Cleaning up..."
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	@echo "Cleanup complete!"

test:
	@echo "Running tests..."
	$(PYTHON_VENV) -m pytest tests/

run-local:
	@echo "Running stock price job locally..."
	$(PYTHON_VENV) main.py stock-price --tickers $(TICKERS) --env local

run-k8s:
	@echo "Running stock price job on Kubernetes..."
	$(PYTHON_VENV) main.py stock-price --tickers $(TICKERS) --env kubernetes

# Development commands
lint:
	@echo "Running linters..."
	$(PYTHON_VENV) -m flake8 .
	$(PYTHON_VENV) -m mypy .

format:
	@echo "Formatting code..."
	$(PYTHON_VENV) -m black .
	$(PYTHON_VENV) -m isort . 