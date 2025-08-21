from flask import Flask, render_template_string, request, jsonify
import requests
import time
import logging
import os
import threading
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
BACKEND_URL = os.getenv('BACKEND_URL', 'http://backend:5001')
APP_VERSION = os.getenv('APP_VERSION', '1.0.0')

# Metrics tracking
request_count = 0
error_count = 0
response_times = []
endpoint_stats = {
    '/': {'count': 0, 'avg_time': 0, 'errors': 0},
    '/health': {'count': 0, 'avg_time': 0, 'errors': 0},
    '/metrics': {'count': 0, 'avg_time': 0, 'errors': 0},
    '/slow': {'count': 0, 'avg_time': 0, 'errors': 0},
    '/error': {'count': 0, 'avg_time': 0, 'errors': 0}
}

def update_endpoint_stats(endpoint, response_time, is_error=False):
    """Update statistics for specific endpoint"""
    if endpoint in endpoint_stats:
        stats = endpoint_stats[endpoint]
        stats['count'] += 1
        if is_error:
            stats['errors'] += 1
        # Update rolling average
        stats['avg_time'] = (stats['avg_time'] + response_time) / 2

def background_load_generator():
    """Generate background traffic to simulate real usage"""
    endpoints = ['/', '/health', '/metrics', '/slow', '/error']
    weights = [50, 20, 10, 15, 5]  # Weighted distribution
    
    while True:
        try:
            # Sleep for random interval (1-5 seconds)
            time.sleep(random.uniform(1, 5))
            
            # Select endpoint based on weights
            endpoint = random.choices(endpoints, weights=weights)[0]
            
            # Make internal request
            try:
                start_time = time.time()
                if endpoint == '/':
                    # Simulate homepage request
                    pass  # Will be handled by actual endpoint
                elif endpoint == '/health':
                    requests.get(f"http://localhost:5000/health", timeout=2)
                elif endpoint == '/metrics':
                    requests.get(f"http://localhost:5000/metrics", timeout=2)
                elif endpoint == '/slow':
                    requests.get(f"http://localhost:5000/slow", timeout=10)
                elif endpoint == '/error':
                    requests.get(f"http://localhost:5000/error", timeout=2)
                
                response_time = time.time() - start_time
                logger.info(f"Background request: {endpoint} completed in {response_time:.3f}s")
                
            except Exception as e:
                logger.warning(f"Background request failed: {endpoint} - {e}")
                
        except Exception as e:
            logger.error(f"Background load generator error: {e}")
            time.sleep(5)

# Start background load generator
load_thread = threading.Thread(target=background_load_generator, daemon=True)
load_thread.start()

@app.route('/')
def home():
    """Enhanced home page with modern UI"""
    global request_count, response_times, error_count
    start_time = time.time()
    request_count += 1
    
    try:
        logger.info(f"Request #{request_count} from {request.remote_addr}")
        
        # Call backend service
        try:
            response = requests.get(f"{BACKEND_URL}/api/data", timeout=5)
            backend_data = response.json()
        except:
            backend_data = {"message": "Backend unavailable"}
        
        # Calculate response time
        response_time = time.time() - start_time
        response_times.append(response_time)
        update_endpoint_stats('/', response_time)
        
        logger.info(f"Request completed in {response_time:.3f}s")
        
        # Modern HTML template with CSS
        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Observability Demo | Real-Time Monitoring</title>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    color: #333;
                    padding: 20px;
                }
                
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    background: rgba(255, 255, 255, 0.95);
                    border-radius: 20px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    overflow: hidden;
                }
                
                .header {
                    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    position: relative;
                }
                
                .header::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="3" fill="rgba(255,255,255,0.1)"/></svg>') repeat;
                    opacity: 0.1;
                }
                
                .header h1 {
                    font-size: 2.5em;
                    margin-bottom: 10px;
                    font-weight: 300;
                    position: relative;
                    z-index: 1;
                }
                
                .status-badge {
                    display: inline-block;
                    padding: 8px 16px;
                    background: #27ae60;
                    border-radius: 20px;
                    font-size: 0.9em;
                    position: relative;
                    z-index: 1;
                }
                
                .pulse {
                    animation: pulse 2s infinite;
                }
                
                @keyframes pulse {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.05); }
                    100% { transform: scale(1); }
                }
                
                .metrics-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    padding: 30px;
                }
                
                .metric-card {
                    background: white;
                    border-radius: 15px;
                    padding: 25px;
                    box-shadow: 0 10px 25px rgba(0,0,0,0.08);
                    border-left: 5px solid #3498db;
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                }
                
                .metric-card:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 15px 35px rgba(0,0,0,0.15);
                }
                
                .metric-card.success { border-left-color: #27ae60; }
                .metric-card.warning { border-left-color: #f39c12; }
                .metric-card.error { border-left-color: #e74c3c; }
                .metric-card.info { border-left-color: #3498db; }
                
                .metric-title {
                    font-size: 1.2em;
                    font-weight: 600;
                    margin-bottom: 15px;
                    color: #2c3e50;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                
                .metric-value {
                    font-size: 2em;
                    font-weight: 700;
                    color: #3498db;
                    margin-bottom: 10px;
                    font-family: 'Courier New', monospace;
                }
                
                .metric-details {
                    font-size: 0.9em;
                    color: #7f8c8d;
                    line-height: 1.6;
                }
                
                .endpoints-section {
                    background: #f8f9fa;
                    padding: 30px;
                    border-top: 1px solid #ecf0f1;
                }
                
                .endpoints-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 15px;
                    margin-top: 20px;
                }
                
                .endpoint-card {
                    background: white;
                    border-radius: 12px;
                    padding: 20px;
                    text-align: center;
                    transition: all 0.3s ease;
                    border: 2px solid transparent;
                    text-decoration: none;
                    color: inherit;
                    display: block;
                }
                
                .endpoint-card:hover {
                    border-color: #3498db;
                    transform: translateY(-3px);
                    text-decoration: none;
                    color: inherit;
                }
                
                .endpoint-emoji {
                    font-size: 2em;
                    margin-bottom: 10px;
                    display: block;
                }
                
                .endpoint-name {
                    font-weight: 600;
                    margin-bottom: 8px;
                    color: #2c3e50;
                }
                
                .endpoint-desc {
                    font-size: 0.85em;
                    color: #7f8c8d;
                    margin-bottom: 10px;
                }
                
                .endpoint-stats {
                    font-size: 0.8em;
                    color: #3498db;
                    font-family: 'Courier New', monospace;
                }
                
                .auto-refresh {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: rgba(0,0,0,0.8);
                    color: white;
                    padding: 10px 15px;
                    border-radius: 25px;
                    font-size: 0.9em;
                    z-index: 1000;
                }
                
                .footer {
                    text-align: center;
                    padding: 20px;
                    background: #34495e;
                    color: #bdc3c7;
                    font-size: 0.9em;
                }
                
                .live-indicator {
                    width: 12px;
                    height: 12px;
                    background: #27ae60;
                    border-radius: 50%;
                    display: inline-block;
                    margin-right: 8px;
                    animation: blink 1s infinite;
                }
                
                @keyframes blink {
                    0%, 50% { opacity: 1; }
                    51%, 100% { opacity: 0.3; }
                }
                
                @media (max-width: 768px) {
                    .metrics-grid {
                        grid-template-columns: 1fr;
                        padding: 20px;
                    }
                    
                    .header h1 {
                        font-size: 2em;
                    }
                }
            </style>
            <script>
                // Auto-refresh every 5 seconds
                setTimeout(() => {
                    window.location.reload();
                }, 5000);
            </script>
        </head>
        <body>
            <div class="auto-refresh">
                <span class="live-indicator"></span>
                Auto-refresh: 5s
            </div>
            
            <div class="container">
                <div class="header">
                    <h1>🔍 Observability Demo</h1>
                    <div class="status-badge pulse">
                        System Operational • v{{ version }}
                    </div>
                </div>
                
                <div class="metrics-grid">
                    <div class="metric-card info">
                        <div class="metric-title">
                            📊 Total Requests
                        </div>
                        <div class="metric-value">{{ req_count }}</div>
                        <div class="metric-details">
                            Session requests processed<br>
                            Last updated: {{ current_time }}
                        </div>
                    </div>
                    
                    <div class="metric-card success">
                        <div class="metric-title">
                            ⚡ Response Time
                        </div>
                        <div class="metric-value">{{ avg_response }}ms</div>
                        <div class="metric-details">
                            Average response time<br>
                            Target: < 200ms
                        </div>
                    </div>
                    
                    <div class="metric-card {{ 'error' if error_count > 0 else 'success' }}">
                        <div class="metric-title">
                            🛡️ Error Rate
                        </div>
                        <div class="metric-value">{{ error_count }}</div>
                        <div class="metric-details">
                            Total errors in session<br>
                            SLA: < 1% error rate
                        </div>
                    </div>
                    
                    <div class="metric-card warning">
                        <div class="metric-title">
                            🔗 Backend Status
                        </div>
                        <div class="metric-value">LIVE</div>
                        <div class="metric-details">
                            {{ backend_info }}<br>
                            Last check: {{ current_time }}
                        </div>
                    </div>
                </div>
                
                <div class="endpoints-section">
                    <h2 style="text-align: center; margin-bottom: 10px; color: #2c3e50;">
                        🎯 Observability Endpoints
                    </h2>
                    <p style="text-align: center; color: #7f8c8d; margin-bottom: 20px;">
                        These endpoints demonstrate monitoring patterns used in enterprise applications
                    </p>
                    
                    <div class="endpoints-grid">
                        <a href="/health" class="endpoint-card">
                            <span class="endpoint-emoji">❤️</span>
                            <div class="endpoint-name">Health Check</div>
                            <div class="endpoint-desc">Kubernetes liveness probe</div>
                            <div class="endpoint-stats">{{ endpoint_stats['/health']['count'] }} requests</div>
                        </a>
                        
                        <a href="/metrics" class="endpoint-card">
                            <span class="endpoint-emoji">📈</span>
                            <div class="endpoint-name">Metrics Export</div>
                            <div class="endpoint-desc">Prometheus-compatible metrics</div>
                            <div class="endpoint-stats">{{ endpoint_stats['/metrics']['count'] }} requests</div>
                        </a>
                        
                        <a href="/slow" class="endpoint-card">
                            <span class="endpoint-emoji">🐌</span>
                            <div class="endpoint-name">Slow Endpoint</div>
                            <div class="endpoint-desc">Performance testing (3s delay)</div>
                            <div class="endpoint-stats">{{ endpoint_stats['/slow']['count'] }} requests</div>
                        </a>
                        
                        <a href="/error" class="endpoint-card">
                            <span class="endpoint-emoji">💥</span>
                            <div class="endpoint-name">Error Simulation</div>
                            <div class="endpoint-desc">Random HTTP errors</div>
                            <div class="endpoint-stats">{{ endpoint_stats['/error']['count'] }} requests</div>
                        </a>
                        
                        <a href="http://localhost:3000" target="_blank" class="endpoint-card" style="border-color: #e74c3c;">
                            <span class="endpoint-emoji">📊</span>
                            <div class="endpoint-name">Grafana Dashboard</div>
                            <div class="endpoint-desc">Real-time monitoring (admin/admin)</div>
                            <div class="endpoint-stats">External Link</div>
                        </a>
                        
                        <a href="http://localhost:9090" target="_blank" class="endpoint-card" style="border-color: #f39c12;">
                            <span class="endpoint-emoji">🔍</span>
                            <div class="endpoint-name">Prometheus</div>
                            <div class="endpoint-desc">Metrics collection</div>
                            <div class="endpoint-stats">External Link</div>
                        </a>
                    </div>
                </div>
                
                <div class="footer">
                    <p>🚀 Built for demonstrating enterprise observability patterns</p>
                    <p>Perfect for understanding how tools like New Relic integrate with microservices</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return render_template_string(html_template,
            version=APP_VERSION,
            current_time=datetime.now().strftime("%H:%M:%S"),
            req_count=request_count,
            backend_info=backend_data.get('message', 'Connected'),
            avg_response=round(sum(response_times) / len(response_times) * 1000, 2) if response_times else 0,
            error_count=error_count,
            endpoint_stats=endpoint_stats
        )
        
    except Exception as e:
        error_count += 1
        response_time = time.time() - start_time
        update_endpoint_stats('/', response_time, is_error=True)
        logger.error(f"Application error: {str(e)}")
        
        return f"""
        <div style="text-align: center; padding: 50px; font-family: Arial, sans-serif;">
            <h1 style="color: #e74c3c;">🚫 Service Error</h1>
            <p>Application error occurred</p>
            <p style="color: #7f8c8d;">Error: {str(e)}</p>
            <a href="/" style="color: #3498db;">← Refresh</a>
        </div>
        """, 500

@app.route('/health')
def health_check():
    """Enhanced health check with detailed status"""
    try:
        start_time = time.time()
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=2)
            response_time = time.time() - start_time
            backend_healthy = response.status_code == 200
        except:
            response_time = time.time() - start_time
            backend_healthy = False
        
        update_endpoint_stats('/health', response_time, not backend_healthy)
        
        health_status = {
            "status": "healthy" if backend_healthy else "degraded",
            "timestamp": datetime.now().isoformat(),
            "version": APP_VERSION,
            "backend_status": "up" if backend_healthy else "down",
            "backend_response_time_ms": round(response_time * 1000, 2),
            "request_count": request_count,
            "error_count": error_count,
            "session_stats": {
                "total_requests": request_count,
                "avg_response_time_ms": round(sum(response_times) / len(response_times) * 1000, 2) if response_times else 0,
                "uptime": "healthy"
            }
        }
        
        status_code = 200 if backend_healthy else 503
        return jsonify(health_status), status_code
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        update_endpoint_stats('/health', 0, is_error=True)
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 503

@app.route('/metrics')
def prometheus_metrics():
    """Prometheus-compatible metrics endpoint"""
    start_time = time.time()
    response_time = time.time() - start_time
    update_endpoint_stats('/metrics', response_time)
    
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    # Prometheus format metrics
    metrics_text = f"""# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{{method="GET",endpoint="/"}} {request_count}

# HELP http_request_duration_seconds HTTP request duration
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_sum {sum(response_times)}
http_request_duration_seconds_count {len(response_times)}

# HELP http_errors_total Total HTTP errors
# TYPE http_errors_total counter
http_errors_total {error_count}

# HELP app_version Application version info
# TYPE app_version gauge
app_version{{version="{APP_VERSION}"}} 1

# HELP endpoint_requests_total Requests per endpoint
# TYPE endpoint_requests_total counter"""

    for endpoint, stats in endpoint_stats.items():
        clean_endpoint = endpoint.replace('/', '_root') if endpoint == '/' else endpoint.replace('/', '_')
        metrics_text += f'\nendpoint_requests_total{{endpoint="{endpoint}"}} {stats["count"]}'

    metrics_text += f"""

# HELP backend_status Backend service status
# TYPE backend_status gauge
backend_status 1
"""
    
    return metrics_text, 200, {'Content-Type': 'text/plain'}

@app.route('/slow')
def slow_endpoint():
    """Enhanced slow endpoint with tracking"""
    start_time = time.time()
    logger.warning("Slow endpoint accessed - simulating performance issue")
    
    # Simulate slow operation
    time.sleep(3)
    
    response_time = time.time() - start_time
    update_endpoint_stats('/slow', response_time)
    
    return jsonify({
        "message": "Slow operation completed",
        "delay_seconds": 3,
        "actual_response_time_ms": round(response_time * 1000, 2),
        "purpose": "Performance monitoring demonstration",
        "timestamp": datetime.now().isoformat(),
        "note": "This endpoint helps demonstrate APM alerting capabilities"
    })

@app.route('/error')
def error_endpoint():
    """Enhanced error endpoint with tracking"""
    start_time = time.time()
    global error_count
    error_count += 1
    
    logger.error("Intentional error triggered for testing")
    
    # Simulate different types of errors randomly
    import random
    error_types = [
        ("Database Connection Error", 503),
        ("Validation Error", 400),
        ("External Service Timeout", 504),
        ("Internal Server Error", 500),
        ("Authentication Failed", 401),
        ("Rate Limit Exceeded", 429)
    ]
    
    error_message, status_code = random.choice(error_types)
    response_time = time.time() - start_time
    update_endpoint_stats('/error', response_time, is_error=True)
    
    return jsonify({
        "error": error_message,
        "status_code": status_code,
        "timestamp": datetime.now().isoformat(),
        "total_errors": error_count,
        "error_rate_percent": round((error_count / request_count) * 100, 2) if request_count > 0 else 0,
        "note": "This endpoint demonstrates error tracking and alerting"
    }), status_code

if __name__ == '__main__':
    logger.info(f"Starting enhanced frontend service version {APP_VERSION}")
    logger.info("Background load generator started - creating realistic traffic patterns")
    app.run(host='0.0.0.0', port=5000, debug=False)