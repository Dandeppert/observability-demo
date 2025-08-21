# Observability Demo - Containerized Microservices

A hands-on demonstration of observability concepts using containerized microservices, built to understand monitoring challenges in modern applications.

## What This Demonstrates

This project showcases enterprise observability patterns including:

- **Microservices Communication** - Frontend service calling backend API
- **Health Check Endpoints** - Kubernetes liveness/readiness probes
- **Metrics Collection** - Prometheus-compatible metrics endpoints
- **Distributed Tracing Scenarios** - Cross-service request tracking
- **Performance Monitoring** - Intentional slow endpoints and latency simulation
- **Error Tracking** - Random error generation and logging
- **Container Orchestration** - Kubernetes deployment patterns

Perfect for understanding how tools like New Relic, DataDog, or Prometheus integrate with real applications.

## Architecture

```
┌─────────────┐    HTTP     ┌─────────────┐
│   Frontend  │ ──────────► │   Backend   │
│   (Flask)   │             │   (Flask)   │
│   Port 5000 │             │   Port 5001 │
└─────────────┘             └─────────────┘
       │                           │
       │                           │
       ▼                           ▼
┌─────────────────────────────────────────┐
│           Kubernetes Cluster            │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │   Service   │  │   Health Checks │   │
│  │  Discovery  │  │   & Monitoring  │   │
│  └─────────────┘  └─────────────────┘   │
└─────────────────────────────────────────┘
```

## Quick Start

### Prerequisites
- Docker Desktop with Kubernetes enabled
- `kubectl` command-line tool
- 5 minutes of your time

### 1. Clone and Build
```bash
git clone https://github.com/yourusername/observability-demo.git
cd observability-demo

# Build Docker images
cd frontend && docker build -t observability-demo/frontend:latest .
cd ../backend && docker build -t observability-demo/backend:latest .
```

### 2. Deploy to Kubernetes
```bash
cd k8s
kubectl apply -f namespace.yaml
kubectl apply -f backend-deployment.yaml
kubectl apply -f frontend-deployment.yaml

# Wait for pods to start
kubectl get pods -n observability-demo -w
```

### 3. Access Application
```bash
# Port forward to access locally
kubectl port-forward service/frontend-service 8080:5000 -n observability-demo
```

Visit: **http://localhost:8080**

## Observability Endpoints

| Endpoint | Purpose | Description |
|----------|---------|-------------|
| `/` | Main Application | Shows real-time metrics and service communication |
| `/health` | Health Checks | Kubernetes liveness/readiness probe endpoint |
| `/metrics` | Metrics Collection | Prometheus-compatible metrics for monitoring tools |
| `/slow` | Performance Testing | 3-second delay to simulate performance issues |
| `/error` | Error Simulation | Random HTTP errors for error rate testing |

## What You'll See

### Main Dashboard
- Real-time request counts and response times
- Backend service connectivity status  
- Cross-service communication metrics
- Performance statistics

### Health Monitoring
```json
{
  "status": "healthy",
  "timestamp": "2025-01-21T10:30:00Z",
  "version": "1.0.0",
  "backend_status": "up",
  "request_count": 42,
  "error_count": 2
}
```

### Metrics Data
```json
{
  "http_requests_total": 156,
  "http_request_errors_total": 8,
  "http_request_duration_seconds_avg": 0.245,
  "app_version": "1.0.0"
}
```

## Learning Objectives

### For DevOps Engineers
- Container orchestration with Kubernetes
- Service discovery and inter-service communication
- Health check implementation patterns
- Metrics exposition for monitoring tools

### For SRE/Platform Teams  
- Observability integration points
- Performance monitoring strategies
- Error rate tracking and alerting scenarios
- Distributed system debugging approaches

### For Monitoring Tool Users
- How applications expose monitoring data
- Integration patterns for APM tools
- Performance bottleneck identification
- Error tracking and alert configuration

## Advanced Usage

### View Real-Time Logs
```bash
# Frontend logs
kubectl logs -f deployment/frontend-deployment -n observability-demo

# Backend logs  
kubectl logs -f deployment/backend-deployment -n observability-demo
```

### Scale Services
```bash
# Scale to 3 frontend replicas
kubectl scale deployment frontend-deployment --replicas=3 -n observability-demo
```

### Load Testing
```bash
# Generate continuous traffic
while true; do curl http://localhost:8080/; sleep 1; done
```

## Extending the Demo

### Add Database Layer
- PostgreSQL for metrics storage
- Database performance monitoring
- Connection pool tracking

### Monitoring Stack Integration
- Prometheus for metrics collection
- Grafana for dashboard visualization
- Jaeger for distributed tracing

### Performance Testing
- Load generator for realistic traffic
- Chaos engineering scenarios
- Resource constraint testing

## Use Cases

### Interview Preparation
Perfect for demonstrating understanding of:
- Container orchestration
- Microservices architecture  
- Observability best practices
- Performance monitoring concepts

### Training Material
Hands-on lab for teaching:
- Docker containerization
- Kubernetes deployment
- Monitoring integration
- DevOps practices

### Proof of Concept
Foundation for building:
- Monitoring strategy demos
- Tool evaluation environments
- Architecture decision discussions

## Cleanup

```bash
# Remove everything
kubectl delete namespace observability-demo

# Or cleanup Docker images
docker rmi observability-demo/frontend:latest
docker rmi observability-demo/backend:latest
```

## Contributing

Contributions welcome! Ideas for enhancement:

- [ ] Add Redis caching layer
- [ ] Implement circuit breaker patterns  
- [ ] Add Prometheus + Grafana stack
- [ ] Create New Relic integration example
- [ ] Add database performance monitoring
- [ ] Implement distributed tracing with Jaeger

## License

MIT License - Feel free to use this for learning, training, or demonstrations.

## Why This Matters

Modern applications are complex, distributed systems where traditional monitoring falls short. This demo provides hands-on experience with the observability challenges that tools like New Relic, DataDog, and Prometheus solve in production environments.

Understanding these patterns is crucial for anyone working with containerized applications, microservices architectures, or platform engineering.

---

**Built with ❤️ for the observability community**