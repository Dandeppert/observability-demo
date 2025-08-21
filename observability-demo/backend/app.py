from flask import Flask, jsonify
import time
import logging
import os
import random
from datetime import datetime

# Configure structured logging - New Relic ingests these logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Service configuration
SERVICE_NAME = "backend-api"
APP_VERSION = os.getenv('APP_VERSION', '1.0.0')

# Simulate database or external service
class MockDatabase:
    """
    Simulates database operations that would be monitored by APM tools
    
    OBSERVABILITY NOTE: In real applications, New Relic tracks:
    - Database query performance
    - Connection pool metrics
    - Slow query identification
    - Database error rates
    """
    
    def __init__(self):
        self.connection_count = 0
        self.query_count = 0
    
    def connect(self):
        """Simulate database connection with random latency"""
        self.connection_count += 1
        # Simulate connection time (New Relic would track this)
        connection_time = random.uniform(0.01, 0.1)  # 10-100ms
        time.sleep(connection_time)
        logger.info(f"Database connected in {connection_time:.3f}s")
        return connection_time
    
    def query(self, query_type="SELECT"):
        """Simulate database query with realistic latency"""
        self.query_count += 1
        
        # Simulate different query performance characteristics
        if query_type == "SELECT":
            query_time = random.uniform(0.005, 0.05)  # 5-50ms for reads
        elif query_type == "INSERT":
            query_time = random.uniform(0.01, 0.1)    # 10-100ms for writes
        else:
            query_time = random.uniform(0.02, 0.2)    # 20-200ms for complex queries
        
        time.sleep(query_time)
        logger.info(f"Database {query_type} completed in {query_time:.3f}s")
        
        # Simulate occasional slow queries (what New Relic would alert on)
        if random.random() < 0.1:  # 10% chance of slow query
            slow_time = random.uniform(0.5, 1.0)
            time.sleep(slow_time)
            logger.warning(f"Slow query detected: additional {slow_time:.3f}s")
        
        return query_time

# Initialize mock database
db = MockDatabase()

@app.route('/api/data')
def get_data():
    """
    Main API endpoint that simulates typical backend operations
    
    OBSERVABILITY NOTE: This endpoint demonstrates:
    - API performance monitoring
    - Database interaction tracking
    - Business logic timing
    - Error handling and logging
    """
    start_time = time.time()
    
    try:
        logger.info("API request received for data endpoint")
        
        # Simulate database operations (New Relic tracks these)
        db.connect()
        db.query("SELECT")
        
        # Simulate business logic processing
        processing_time = random.uniform(0.01, 0.05)
        time.sleep(processing_time)
        
        # Calculate total response time
        total_time = time.time() - start_time
        
        response_data = {
            "service": SERVICE_NAME,
            "version": APP_VERSION,
            "message": "Data retrieved successfully",
            "timestamp": datetime.now().isoformat(),
            "processing_time_ms": round(total_time * 1000, 2),
            "database_queries": db.query_count,
            "database_connections": db.connection_count,
            "status": "success"
        }
        
        logger.info(f"API request completed in {total_time:.3f}s")
        return jsonify(response_data)
        
    except Exception as e:
        # Error handling - New Relic tracks exceptions and error rates
        logger.error(f"API error: {str(e)}")
        return jsonify({
            "service": SERVICE_NAME,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "status": "error"
        }), 500

@app.route('/health')
def health_check():
    """
    Health check endpoint for Kubernetes probes
    
    OBSERVABILITY NOTE: Kubernetes uses this for:
    - Liveness probes (restart container if unhealthy)
    - Readiness probes (remove from load balancer if not ready)
    New Relic monitors these to track service availability
    """
    try:
        # Test database connectivity as part of health check
        connection_time = db.connect()
        
        health_data = {
            "service": SERVICE_NAME,
            "status": "healthy",
            "version": APP_VERSION,
            "timestamp": datetime.now().isoformat(),
            "database_status": "connected",
            "database_connection_time_ms": round(connection_time * 1000, 2),
            "uptime_checks": db.connection_count
        }
        
        return jsonify(health_data), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "service": SERVICE_NAME,
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 503

@app.route('/metrics')
def metrics():
    """
    Metrics endpoint for monitoring systems
    
    OBSERVABILITY NOTE: This exposes application metrics that monitoring
    tools like New Relic, Prometheus, or DataDog can scrape
    """
    metrics_data = {
        "service_name": SERVICE_NAME,
        "version": APP_VERSION,
        "database_connections_total": db.connection_count,
        "database_queries_total": db.query_count,
        "timestamp": datetime.now().isoformat(),
        "uptime": "healthy"  # In production, this would be actual uptime
    }
    
    return jsonify(metrics_data)

@app.route('/api/slow')
def slow_api():
    """
    Intentionally slow endpoint for testing performance monitoring
    
    OBSERVABILITY NOTE: This simulates the type of performance bottleneck
    that New Relic's APM would identify and alert on
    """
    logger.warning("Slow API endpoint accessed")
    
    # Simulate slow external service call
    time.sleep(2)
    
    # Simulate multiple slow database queries
    db.query("COMPLEX_JOIN")
    db.query("COMPLEX_JOIN")
    
    return jsonify({
        "message": "Slow operation completed",
        "delay_seconds": 2,
        "purpose": "Performance testing",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    logger.info(f"Starting {SERVICE_NAME} version {APP_VERSION}")
    app.run(host='0.0.0.0', port=5001, debug=False)