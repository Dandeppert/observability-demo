from flask import Flask, render_template_string, request, jsonify
import requests
import time
import logging
import os
from datetime import datetime

# Configure logging - This is what New Relic would collect as "Logs" in MELT
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Environment variables - Common in container environments
BACKEND_URL = os.getenv('BACKEND_URL', 'http://backend-service:5001')
APP_VERSION = os.getenv('APP_VERSION', '1.0.0')

# Global variables to simulate metrics - New Relic would collect these as "Metrics"
request_count = 0
error_count = 0
response_times = []

@app.route('/')
def home():
    """
    Main application endpoint
    
    OBSERVABILITY NOTE: This demonstrates a typical user journey that would
    generate traces in New Relic showing the full request path from frontend
    to backend services.
    """
    global request_count, response_times
    start_time = time.time()
    request_count += 1
    
    try:
        # Log the incoming request - New Relic collects these logs
        logger.info(f"Received request #{request_count} from {request.remote_addr}")
        
        # Call backend service - This creates a distributed trace
        # New Relic would track this cross-service communication
        response = requests.get(f"{BACKEND_URL}/api/data", timeout=5)
        backend_data = response.json()
        
        # Calculate response time - Key performance metric
        response_time = time.time() - start_time
        response_times.append(response_time)
        
        # Log successful transaction
        logger.info(f"Request completed in {response_time:.3f}s")
        
        # Render response with backend data
        html_template = """
        <html>
        <head><title>Observability Demo App</title></head>
        <body style="font-family: Arial, sans-serif; margin: 40px;">
            <h1>🔍 Observability Demo Application</h1>
            <p><strong>Frontend Version:</strong> {{ version }}</p>
            <p><strong>Current Time:</strong> {{ current_time }}</p>
            <p><strong>Request Count:</strong> {{ req_count }}</p>
            <p><strong>Backend Data:</strong> {{ backend_info }}</p>
            <p><strong>Average Response Time:</strong> {{ avg_response }}ms</p>
            
            <h3>Monitoring Endpoints:</h3>
            <ul>
                <li><a href="/health">Health Check</a> - Kubernetes liveness probe</li>
                <li><a href="/metrics">Application Metrics</a> - What APM tools collect</li>
                <li><a href="/slow">Slow Endpoint</a> - Simulates performance issues</li>
                <li><a href="/error">Error Endpoint</a> - Simulates failures</li>
            </ul>
            
            <p><em>This demonstrates the type of web application New Relic customers monitor for performance, errors, and user experience.</em></p>
        </body>
        </html>
        """
        
        return render_template_string(html_template,
            version=APP_VERSION,
            current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            req_count=request_count,
            backend_info=backend_data.get('message', 'No data'),
            avg_response=round(sum(response_times) / len(response_times) * 1000, 2) if response_times else 0
        )
        
    except requests.RequestException as e:
        # Handle backend service failures - Common in microservices
        global error_count
        error_count += 1
        logger.error(f"Backend service error: {str(e)}")
        
        return f"<h1>Service Error</h1><p>Backend service unavailable: {str(e)}</p>", 503

@app.route('/health')
def health_check():
    """
    Kubernetes health check endpoint
    
    OBSERVABILITY NOTE: This is what Kubernetes uses for liveness/readiness probes.
    New Relic monitors these to understand service health and availability.
    """
    try:
        # Test backend connectivity as part of health check
        response = requests.get(f"{BACKEND_URL}/health", timeout=2)
        backend_healthy = response.status_code == 200
        
        health_status = {
            "status": "healthy" if backend_healthy else "degraded",
            "timestamp": datetime.now().isoformat(),
            "version": APP_VERSION,
            "backend_status": "up" if backend_healthy else "down",
            "request_count": request_count,
            "error_count": error_count
        }
        
        status_code = 200 if backend_healthy else 503
        return jsonify(health_status), status_code
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 503

@app.route('/metrics')
def metrics():
    """
    Application metrics endpoint
    
    OBSERVABILITY NOTE: This simulates Prometheus-style metrics that APM tools
    like New Relic collect. In production, this would be much more detailed.
    """
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    metrics_data = {
        "http_requests_total": request_count,
        "http_request_errors_total": error_count,
        "http_request_duration_seconds_avg": avg_response_time,
        "app_version": APP_VERSION,
        "timestamp": datetime.now().isoformat()
    }
    
    logger.info("Metrics endpoint accessed")
    return jsonify(metrics_data)

@app.route('/slow')
def slow_endpoint():
    """
    Simulates a slow-performing endpoint
    
    OBSERVABILITY NOTE: This demonstrates the type of performance issue that
    New Relic's APM would identify through transaction tracing and alerting.
    """
    logger.warning("Slow endpoint accessed - simulating performance issue")
    
    # Simulate slow database query or external API call
    time.sleep(3)  # 3-second delay
    
    return jsonify({
        "message": "This endpoint intentionally slow (3s delay)",
        "purpose": "Demonstrates performance monitoring capabilities",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/error')
def error_endpoint():
    """
    Simulates application errors
    
    OBSERVABILITY NOTE: This demonstrates error tracking and alerting
    capabilities that New Relic provides.
    """
    global error_count
    error_count += 1
    
    logger.error("Intentional error triggered for testing")
    
    # Simulate different types of errors randomly
    import random
    error_types = [
        ("Database Connection Error", 503),
        ("Validation Error", 400),
        ("External Service Timeout", 504),
        ("Internal Server Error", 500)
    ]
    
    error_message, status_code = random.choice(error_types)
    
    return jsonify({
        "error": error_message,
        "timestamp": datetime.now().isoformat(),
        "total_errors": error_count
    }), status_code

if __name__ == '__main__':
    logger.info(f"Starting frontend service version {APP_VERSION}")
    # Run on all interfaces so Kubernetes can reach it
    app.run(host='0.0.0.0', port=5000, debug=False)