from flask import Flask, jsonify
import time
import logging
import os
import random
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Environment variables
APP_VERSION = os.getenv('APP_VERSION', '1.0.0')

# Metrics tracking
request_count = 0
error_count = 0
response_times = []
start_time = time.time()  # Track service start time

@app.route('/health')
def health_check():
    """Health check endpoint"""
    global request_count
    request_count += 1
    
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": APP_VERSION,
        "service": "backend-api",
        "uptime": "operational"
    }), 200

@app.route('/api/data')
def get_data():
    """Main API endpoint that frontend calls"""
    global request_count, response_times
    start_time = time.time()
    request_count += 1
    
    # Simulate some processing time
    processing_time = random.uniform(0.1, 0.5)
    time.sleep(processing_time)
    
    response_time = time.time() - start_time
    response_times.append(response_time)
    
    logger.info(f"API request #{request_count} completed in {response_time:.3f}s")
    
    return jsonify({
        "message": "Backend API Connected",
        "timestamp": datetime.now().isoformat(),
        "version": APP_VERSION,
        "request_id": request_count,
        "response_time_ms": round(response_time * 1000, 2),
        "status": "success"
    })

@app.route('/metrics')
def prometheus_metrics():
    """Prometheus-compatible metrics endpoint - returns TEXT format"""
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    # Prometheus format metrics (must be text/plain content type)
    metrics_text = f"""# HELP backend_requests_total Total backend requests
# TYPE backend_requests_total counter
backend_requests_total {request_count}

# HELP backend_request_duration_seconds Backend request duration
# TYPE backend_request_duration_seconds histogram
backend_request_duration_seconds_sum {sum(response_times)}
backend_request_duration_seconds_count {len(response_times)}

# HELP backend_errors_total Total backend errors
# TYPE backend_errors_total counter
backend_errors_total {error_count}

# HELP backend_version Backend version info
# TYPE backend_version gauge
backend_version{{version="{APP_VERSION}"}} 1

# HELP backend_uptime_seconds Backend uptime in seconds
# TYPE backend_uptime_seconds gauge
backend_uptime_seconds {time.time()}

# HELP backend_avg_response_time_seconds Average response time
# TYPE backend_avg_response_time_seconds gauge
backend_avg_response_time_seconds {avg_response_time}
"""
    
    # IMPORTANT: Must return text/plain content type for Prometheus
    return metrics_text, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/api/slow')
def slow_api():
    """Slow API endpoint for testing"""
    global request_count
    request_count += 1
    
    # Simulate slow operation
    time.sleep(2)
    
    return jsonify({
        "message": "Slow API operation completed",
        "delay_seconds": 2,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/error')
def error_api():
    """Error API endpoint for testing"""
    global request_count, error_count
    request_count += 1
    error_count += 1
    
    # Random error simulation
    error_types = [
        ("Database timeout", 503),
        ("Validation failed", 400),
        ("Service unavailable", 503),
        ("Internal error", 500)
    ]
    
    error_msg, status_code = random.choice(error_types)
    
    logger.error(f"API error: {error_msg}")
    
    return jsonify({
        "error": error_msg,
        "timestamp": datetime.now().isoformat(),
        "total_errors": error_count
    }), status_code

@app.route('/')
def root():
    """Root endpoint"""
    return jsonify({
        "service": "Observability Demo Backend",
        "version": APP_VERSION,
        "status": "running",
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "data": "/api/data",
            "slow": "/api/slow", 
            "error": "/api/error"
        }
    })

if __name__ == '__main__':
    logger.info(f"Starting backend service version {APP_VERSION}")
    app.run(host='0.0.0.0', port=5001, debug=False)