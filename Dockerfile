# Dockerfile for Auth Service
# Multi-stage build for production-ready Python FastAPI app

FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies (including curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose port (default 8001, can be overridden with PORT env var)
EXPOSE 8001

# Health check - uses curl and respects PORT env var
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8001}/api/v1/health || exit 1

# Run application - reads PORT and HOST from environment
# Using 'exec' to make uvicorn PID 1 for proper signal handling
CMD exec uvicorn app.main:app --host ${HOST:-0.0.0.0} --port ${PORT:-8001}


