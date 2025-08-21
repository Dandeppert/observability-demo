# Use official Python runtime as base image
# Alpine Linux keeps container size small - important for Kubernetes efficiency
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Copy requirements first for better Docker layer caching
# This optimization technique is common in containerized applications
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir reduces image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Create non-root user for security (Kubernetes best practice)
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
USER appuser

# Expose port that the app runs on
# This must match the port in your Kubernetes service definition
EXPOSE 5000

# Health check for Docker/Kubernetes
# This command tests if the container is healthy
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Command to run the application
# Using gunicorn for production-grade WSGI server
CMD ["python", "app.py"]