#!/bin/bash

# DDGS API Startup Script

set -e

echo "🚀 Starting DDGS API..."

# Sync dependencies
echo "📦 Syncing dependencies with uv..."
uv sync --dev --extra api

# Run the API
echo "🌐 Starting FastAPI server on http://localhost:8000"
echo "📚 API documentation available at http://localhost:8000/docs"
echo "🔍 ReDoc documentation available at http://localhost:8000/redoc"

uv run python start_api.py
