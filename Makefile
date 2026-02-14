.PHONY: help setup lint format test all clean

help:
	@echo "Targets:"
	@echo "  setup   - sync uv environment with dev dependencies"
	@echo "  lint    - run ruff check and ty"
	@echo "  format  - run ruff format"
	@echo "  test    - run pytest"
	@echo "  all     - run setup, lint, format and test"
	@echo "  clean   - remove cache and build artifacts"

setup:
	uv sync --dev

lint:
	uv run ruff check --fix
	uv run ty check .

format:
	uv run ruff format

test:
	uv run pytest

all: setup lint format test

clean:
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -name __pycache__ -exec rm -rf {} +
	rm -f uv.lock
