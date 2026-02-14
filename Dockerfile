# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:${PATH}"

# Install system dependencies including curl for healthcheck
RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv and copy application code
RUN pip install --no-cache-dir uv
COPY . .

# Install Python dependencies (including API dependencies)
RUN uv sync --extra api

# Expose port
EXPOSE 8000

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Run the application
CMD ["uv", "run", "python", "start_api.py"]
