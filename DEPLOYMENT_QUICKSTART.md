# Quick Start Deployment Guide

Quick reference for deploying the Appointment Service using Docker or Minikube.

## 🐳 Docker Deployment (Easiest)

### Prerequisites
- Docker Desktop or Docker Engine
- Docker Compose

### Steps

```bash
# 1. Navigate to project root
cd scalable_assignment

# 2. Start all services
docker-compose up --build

# 3. Test the API
curl http://localhost:5001/health

# 4. Stop services
docker-compose down
```

**That's it!** The service will be available at `http://localhost:5001`

## ☸️ Minikube Deployment

### Prerequisites
- Minikube installed
- kubectl installed

### Steps

```bash
# 1. Start Minikube
minikube start

# 2. Build Docker image in Minikube
eval $(minikube docker-env)
docker build -t appointment-service:latest -f appointment-service/Dockerfile appointment-service/

# 3. Deploy to Kubernetes
kubectl apply -f kubernetes/mysql-secret.yaml
kubectl apply -f kubernetes/jwt-secret.yaml
kubectl apply -f kubernetes/mysql-deployment.yaml
kubectl apply -f kubernetes/appointment-service-deployment.yaml

# 4. Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app=mysql --timeout=300s
kubectl wait --for=condition=ready pod -l app=appointment-service --timeout=300s

# 5. Access the service
kubectl port-forward service/appointment-service 5001:5001

# 6. Test the API
curl http://localhost:5001/health
```

## 📝 Quick Commands Reference

### Docker

```bash
# Start
docker-compose up -d

# View logs
docker-compose logs -f appointment-service

# Stop
docker-compose down

# Rebuild
docker-compose up --build -d
```

### Minikube

```bash
# Check status
kubectl get pods
kubectl get services

# View logs
kubectl logs -l app=appointment-service

# Port forward
kubectl port-forward service/appointment-service 5001:5001

# Scale
kubectl scale deployment appointment-service --replicas=3

# Cleanup
kubectl delete -f kubernetes/
```

## 🔗 API Endpoints

- **Health**: `GET http://localhost:5001/health`
- **Register**: `POST http://localhost:5001/api/auth/register`
- **Login**: `POST http://localhost:5001/api/auth/login`
- **Book Appointment**: `POST http://localhost:5001/api/v1/appointments`

## 📚 Full Documentation

- **Docker**: See [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)
- **Minikube**: See [MINIKUBE_DEPLOYMENT.md](MINIKUBE_DEPLOYMENT.md)
- **Kubernetes**: See [kubernetes/README.md](kubernetes/README.md)

## 🆘 Troubleshooting

### Docker: Port already in use
```bash
# Change port in docker-compose.yml
ports:
  - "5002:5001"
```

### Minikube: Image not found
```bash
# Rebuild image in Minikube
eval $(minikube docker-env)
docker build -t appointment-service:latest -f appointment-service/Dockerfile appointment-service/
```

### Database connection failed
```bash
# Check MySQL logs
docker logs appointment-mysql  # Docker
kubectl logs -l app=mysql      # Minikube
```

