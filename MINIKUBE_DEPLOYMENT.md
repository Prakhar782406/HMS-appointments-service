# Minikube Deployment Guide

This guide explains how to deploy the Appointment Service on Minikube (local Kubernetes cluster).

## Prerequisites

- Minikube installed ([Installation Guide](https://minikube.sigs.k8s.io/docs/start/))
- kubectl installed ([Installation Guide](https://kubernetes.io/docs/tasks/tools/))
- Docker Desktop or Docker Engine (Minikube uses Docker driver)

## Quick Start

### 1. Start Minikube

```bash
# Start Minikube cluster
minikube start

# Verify cluster is running
minikube status

# Enable addons (optional but recommended)
minikube addons enable ingress
minikube addons enable metrics-server
```

### 2. Build Docker Image in Minikube

Since Minikube has its own Docker daemon, you need to build the image inside Minikube:

```bash
# Set Docker environment to use Minikube's Docker daemon
eval $(minikube docker-env)

# Build the Docker image
cd appointment-service
docker build -t appointment-service:latest .

# Verify image was created
docker images | grep appointment-service
```

**Note:** On Windows PowerShell, use:
```powershell
minikube docker-env | Invoke-Expression
```

### 3. Deploy to Minikube

```bash
# Navigate to project root
cd /path/to/scalable_assignment

# Deploy secrets
kubectl apply -f kubernetes/mysql-secret.yaml
kubectl apply -f kubernetes/jwt-secret.yaml

# Deploy MySQL
kubectl apply -f kubernetes/mysql-deployment.yaml

# Wait for MySQL to be ready
kubectl wait --for=condition=ready pod -l app=mysql --timeout=300s

# Deploy Appointment Service
kubectl apply -f kubernetes/appointment-service-deployment.yaml

# Wait for service to be ready
kubectl wait --for=condition=ready pod -l app=appointment-service --timeout=300s
```

### 4. Access the Service

```bash
# Get service URL
minikube service appointment-service --url

# Or use port-forward for direct access
kubectl port-forward service/appointment-service 5001:5001

# Test health endpoint
curl http://localhost:5001/health
```

## Step-by-Step Deployment

### Step 1: Start Minikube

```bash
# Start Minikube with specific resources (recommended)
minikube start --memory=4096 --cpus=2

# Check cluster status
kubectl cluster-info
kubectl get nodes
```

### Step 2: Build Docker Image

```bash
# Point Docker client to Minikube's Docker daemon
eval $(minikube docker-env)

# Build image
docker build -t appointment-service:latest -f appointment-service/Dockerfile appointment-service/

# Verify
docker images appointment-service
```

### Step 3: Create Secrets

```bash
# Create MySQL secret
kubectl apply -f kubernetes/mysql-secret.yaml

# Create JWT secret
kubectl apply -f kubernetes/jwt-secret.yaml

# Verify secrets
kubectl get secrets
kubectl describe secret mysql-secret
kubectl describe secret jwt-secret
```

### Step 4: Deploy MySQL

```bash
# Deploy MySQL
kubectl apply -f kubernetes/mysql-deployment.yaml

# Check deployment status
kubectl get deployments
kubectl get pods -l app=mysql

# Wait for MySQL to be ready
kubectl wait --for=condition=ready pod -l app=mysql --timeout=300s

# Check MySQL logs
kubectl logs -l app=mysql
```

### Step 5: Deploy Appointment Service

```bash
# Deploy appointment service
kubectl apply -f kubernetes/appointment-service-deployment.yaml

# Check deployment status
kubectl get deployments
kubectl get pods -l app=appointment-service

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app=appointment-service --timeout=300s

# Check service logs
kubectl logs -l app=appointment-service
```

### Step 6: Verify Deployment

```bash
# Check all resources
kubectl get all

# Check pods
kubectl get pods

# Check services
kubectl get services

# Check persistent volumes
kubectl get pv
kubectl get pvc
```

## Accessing the Service

### Method 1: Port Forwarding (Recommended for Testing)

```bash
# Port forward to access service
kubectl port-forward service/appointment-service 5001:5001

# In another terminal, test the API
curl http://localhost:5001/health
```

### Method 2: Minikube Service

```bash
# Get service URL
minikube service appointment-service --url

# Or open in browser
minikube service appointment-service
```

### Method 3: NodePort (Already Configured)

The service is configured as ClusterIP. To expose via NodePort:

```bash
# Edit service to use NodePort
kubectl patch service appointment-service -p '{"spec":{"type":"NodePort"}}'

# Get NodePort
kubectl get service appointment-service

# Access via Minikube IP
minikube ip
# Then access: http://<minikube-ip>:<node-port>
```

## Useful Commands

### View Logs

```bash
# View appointment service logs
kubectl logs -l app=appointment-service

# View specific pod logs
kubectl logs <pod-name>

# Follow logs
kubectl logs -f -l app=appointment-service

# View MySQL logs
kubectl logs -l app=mysql
```

### Check Pod Status

```bash
# Get all pods
kubectl get pods

# Get pod details
kubectl describe pod <pod-name>

# Check pod events
kubectl get events --sort-by='.lastTimestamp'
```

### Debugging

```bash
# Execute command in pod
kubectl exec -it <pod-name> -- bash

# Test MySQL connection from appointment service pod
kubectl exec -it <appointment-pod-name> -- \
  python -c "import pymysql; pymysql.connect(host='mysql-service', user='root', password='root', database='appointment_db')"

# Check environment variables
kubectl exec <pod-name> -- env
```

### Scaling

```bash
# Scale appointment service
kubectl scale deployment appointment-service --replicas=3

# Check scaled pods
kubectl get pods -l app=appointment-service
```

### Restart Deployment

```bash
# Restart deployment
kubectl rollout restart deployment/appointment-service

# Check rollout status
kubectl rollout status deployment/appointment-service
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods

# Describe pod for details
kubectl describe pod <pod-name>

# Check events
kubectl get events --field-selector involvedObject.name=<pod-name>
```

### Database Connection Issues

```bash
# Check MySQL pod logs
kubectl logs -l app=mysql

# Test MySQL connection
kubectl exec -it <mysql-pod-name> -- mysql -u root -proot -e "SHOW DATABASES;"

# Check MySQL service
kubectl get service mysql-service
kubectl describe service mysql-service
```

### Image Pull Errors

```bash
# Verify image exists in Minikube
eval $(minikube docker-env)
docker images | grep appointment-service

# Rebuild image if needed
docker build -t appointment-service:latest -f appointment-service/Dockerfile appointment-service/

# Delete pods to force restart
kubectl delete pods -l app=appointment-service
```

### Persistent Volume Issues

```bash
# Check PVC status
kubectl get pvc

# Check PV status
kubectl get pv

# Describe PVC for details
kubectl describe pvc mysql-pvc
```

### Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints appointment-service

# Check service configuration
kubectl describe service appointment-service

# Test service from within cluster
kubectl run -it --rm debug --image=busybox --restart=Never -- \
  wget -qO- http://appointment-service:5001/health
```

## Cleanup

### Remove Deployment

```bash
# Delete deployment and service
kubectl delete -f kubernetes/appointment-service-deployment.yaml
kubectl delete -f kubernetes/mysql-deployment.yaml

# Delete secrets
kubectl delete -f kubernetes/mysql-secret.yaml
kubectl delete -f kubernetes/jwt-secret.yaml
```

### Stop Minikube

```bash
# Stop Minikube (preserves cluster state)
minikube stop

# Delete Minikube cluster (removes everything)
minikube delete
```

## Production Considerations

1. **Image Registry**: Use a container registry (Docker Hub, GCR, ECR) instead of local images
2. **Resource Limits**: Adjust resource requests/limits based on workload
3. **Persistent Storage**: Use cloud storage for production (not local volumes)
4. **Secrets Management**: Use external secrets management (HashiCorp Vault, AWS Secrets Manager)
5. **Monitoring**: Set up monitoring and logging (Prometheus, Grafana, ELK)
6. **Ingress**: Configure Ingress controller for external access
7. **SSL/TLS**: Enable SSL/TLS for all connections
8. **Backup**: Implement automated database backups

## Minikube Dashboard

```bash
# Enable dashboard
minikube dashboard

# Or access via URL
minikube dashboard --url
```

## Updating Deployment

### Update Code

```bash
# Rebuild image
eval $(minikube docker-env)
docker build -t appointment-service:latest -f appointment-service/Dockerfile appointment-service/

# Restart deployment
kubectl rollout restart deployment/appointment-service

# Or delete pods to force recreation
kubectl delete pods -l app=appointment-service
```

### Update Configuration

```bash
# Edit deployment
kubectl edit deployment appointment-service

# Or apply updated YAML
kubectl apply -f kubernetes/appointment-service-deployment.yaml
```

## Next Steps

- Set up Ingress for external access
- Configure monitoring and alerting
- Set up CI/CD pipeline
- Implement backup strategies
- Configure auto-scaling

