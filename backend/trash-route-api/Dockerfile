FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for pyrosm/geopandas
RUN apt-get update && apt-get install -y \
    libgeos-dev \
    libexpat1-dev \
    zlib1g-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only necessary requirements files
COPY requirements.txt /app/requirements-root.txt
COPY backend/trash-route-api/requirements.txt /app/requirements-api.txt

# Install root dependencies first (for src/route_generator)
RUN pip install --no-cache-dir -r /app/requirements-root.txt || true

# Install API-specific dependencies
RUN pip install --no-cache-dir -r /app/requirements-api.txt

# Copy only necessary source code (not entire directory)
# Copy src/ directory for route generator
COPY src/ /app/src/

# Copy backend API code only
COPY backend/trash-route-api/app/ /app/backend/trash-route-api/app/
COPY backend/trash-route-api/requirements.txt /app/backend/trash-route-api/requirements.txt

# Set Python path to include app directory for imports
ENV PYTHONPATH=/app:/app/src:$PYTHONPATH

# Create data directories
RUN mkdir -p /app/data/uploads /app/data/outputs

# Expose port
EXPOSE 8003

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8003/health || exit 1

# Run the application
CMD ["uvicorn", "backend.trash-route-api.app.main:app", "--host", "0.0.0.0", "--port", "8003"]
