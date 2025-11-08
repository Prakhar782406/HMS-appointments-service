# Kubernetes Deployment Guide

This directory contains Kubernetes manifests for deploying the Appointment Service.

## Prerequisites

- Kubernetes cluster (v1.19+)
- kubectl configured to connect to your cluster
- PersistentVolume support in your cluster

## Deployment Order

Deploy the resources in the following order:

1. **Secrets** - MySQL password and JWT secret key
2. **MySQL** - Database deployment with persistent storage
3. **Appointment Service** - Application deployment

## Step-by-Step Deployment

### 1. Create Secrets

```bash
# Create MySQL secret
kubectl apply -f mysql-secret.yaml

# Create JWT secret
kubectl apply -f jwt-secret.yaml
```

### 2. Deploy MySQL

```bash
# Deploy MySQL database
kubectl apply -f mysql-deployment.yaml

# Wait for MySQL to be ready
kubectl wait --for=condition=ready pod -l app=mysql --timeout=300s
```

### 3. Deploy Appointment Service

```bash
# Deploy appointment service
kubectl apply -f appointment-service-deployment.yaml

# Wait for service to be ready
kubectl wait --for=condition=ready pod -l app=appointment-service --timeout=300s
```

## Quick Deploy (All at Once)

```bash
# Deploy all resources
kubectl apply -f mysql-secret.yaml
kubectl apply -f jwt-secret.yaml
kubectl apply -f mysql-deployment.yaml
kubectl apply -f appointment-service-deployment.yaml
```

## Verify Deployment

### Check Pods

```bash
# Check all pods
kubectl get pods

# Check MySQL pod
kubectl get pods -l app=mysql

# Check Appointment Service pods
kubectl get pods -l app=appointment-service
```

### Check Services

```bash
# Check all services
kubectl get services

# Check MySQL service
kubectl get service mysql-service

# Check Appointment Service
kubectl get service appointment-service
```

### Check Logs

```bash
# View MySQL logs
kubectl logs -l app=mysql

# View Appointment Service logs
kubectl logs -l app=appointment-service

# View logs for a specific pod
kubectl logs <pod-name>
```

### Test Health Endpoint

```bash
# Port forward to access the service
kubectl port-forward service/appointment-service 5001:5001

# In another terminal, test health endpoint
curl http://localhost:5001/health
```

## Accessing the Service

### Port Forward (Local Testing)

```bash
kubectl port-forward service/appointment-service 5001:5001
```

Then access the service at `http://localhost:5001`

### NodePort (Optional)

To expose the service externally via NodePort, update the service type:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: appointment-service
spec:
  type: NodePort  # Change from ClusterIP to NodePort
  ports:
  - port: 5001
    nodePort: 30001  # Optional: specify node port
    targetPort: 5001
  selector:
    app: appointment-service
```

### LoadBalancer (Cloud Providers)

For cloud providers, use LoadBalancer type:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: appointment-service
spec:
  type: LoadBalancer
  ports:
  - port: 5001
    targetPort: 5001
  selector:
    app: appointment-service
```

## Configuration

### Environment Variables

The following environment variables are configured:

- **MySQL Configuration**:
  - `MYSQL_HOST`: mysql-service
  - `MYSQL_PORT`: 3306
  - `MYSQL_USER`: root
  - `MYSQL_PASSWORD`: From mysql-secret
  - `MYSQL_DATABASE`: appointment_db

- **JWT Configuration**:
  - `JWT_SECRET_KEY`: From jwt-secret
  - `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`: 1440 (24 hours)
  - `JWT_REFRESH_TOKEN_EXPIRE_DAYS`: 30

- **External Services**:
  - `DOCTOR_SERVICE_URL`: http://doctor-service:5001
  - `PATIENT_SERVICE_URL`: http://patient-service:5000

### Updating Secrets

To update secrets:

```bash
# Update MySQL password
kubectl create secret generic mysql-secret \
  --from-literal=password=your-new-password \
  --dry-run=client -o yaml | kubectl apply -f -

# Update JWT secret
kubectl create secret generic jwt-secret \
  --from-literal=secret-key=your-new-secret-key \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart pods to pick up new secrets
kubectl rollout restart deployment/appointment-service
```

## Scaling

### Scale Appointment Service

```bash
# Scale to 3 replicas
kubectl scale deployment appointment-service --replicas=3

# Or edit the deployment
kubectl edit deployment appointment-service
```

### Auto-scaling (HPA)

```bash
# Create HorizontalPodAutoscaler
kubectl autoscale deployment appointment-service \
  --cpu-percent=70 \
  --min=2 \
  --max=10
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name>

# Check events
kubectl get events --sort-by='.lastTimestamp'
```

### Database Connection Issues

```bash
# Check MySQL pod logs
kubectl logs -l app=mysql

# Test MySQL connection from appointment service pod
kubectl exec -it <appointment-service-pod> -- \
  mysql -h mysql-service -u root -proot -e "SHOW DATABASES;"
```

### Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints appointment-service

# Check service configuration
kubectl describe service appointment-service
```

## Cleanup

To remove all resources:

```bash
# Delete deployments and services
kubectl delete -f appointment-service-deployment.yaml
kubectl delete -f mysql-deployment.yaml

# Delete secrets (optional)
kubectl delete -f jwt-secret.yaml
kubectl delete -f mysql-secret.yaml
```

## Production Considerations

1. **Secrets Management**: Use a secrets management solution like HashiCorp Vault or cloud provider secrets manager
2. **Persistent Storage**: Ensure PersistentVolumes are backed up regularly
3. **Resource Limits**: Adjust resource requests/limits based on your workload
4. **Monitoring**: Set up monitoring and alerting for the services
5. **Backup**: Implement regular database backups
6. **SSL/TLS**: Use SSL/TLS for database connections in production
7. **Network Policies**: Implement network policies for security
8. **Ingress**: Use Ingress controller for external access instead of NodePort/LoadBalancer

## Notes

- MySQL root password is stored in a Kubernetes secret. Change it for production.
- JWT secret key is stored in a Kubernetes secret. Use a strong, randomly generated key in production.
- The MySQL PersistentVolumeClaim requests 1Gi of storage. Adjust based on your needs.
- Default admin user credentials: `admin/admin123` (created automatically on first startup)

