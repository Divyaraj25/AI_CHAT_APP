FROM python:3.9-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /app/data /app/logs \
    && chmod -R 777 /app/data /app/logs

# Upgrade pip and setuptools
RUN pip install --no-cache-dir --upgrade pip setuptools

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --retries 5 -r requirements.txt

# Copy application code
COPY backend/ .
COPY frontend/ ../frontend/
COPY data/ ../data/
COPY .env .

# Create directories for data and logs
RUN mkdir -p /app/data /app/logs

# Expose the port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Run the application with development settings
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000", "--debug"]