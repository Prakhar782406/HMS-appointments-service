# Docker Deployment Guide

This guide explains how to run the Appointment Service using Docker.

## Prerequisites

- Docker Desktop or Docker Engine (v20.10+)
- Docker Compose (v2.0+)

## Quick Start

### 1. Build and Run with Docker Compose

```bash
# Navigate to project root
cd /path/to/scalable_assignment

# Build and start all services
docker-compose up --build
```

This will:
- Build the appointment-service Docker image
- Start MySQL database container
- Start appointment-service container
- Wait for MySQL to be ready before starting the service

### 2. Run in Detached Mode

```bash
# Start services in background
docker-compose up -d --build

# View logs
docker-compose logs -f appointment-service

# View all logs
docker-compose logs -f
```

### 3. Stop Services

```bash
# Stop services (keeps volumes)
docker-compose down

# Stop and remove volumes (deletes database data)
docker-compose down -v
```

## Manual Docker Commands

### Build Docker Image

```bash
# Build the appointment service image
cd appointment-service
docker build -t appointment-service:latest .

# Or from project root
docker build -t appointment-service:latest -f appointment-service/Dockerfile appointment-service/
```

### Run MySQL Container

```bash
docker run -d \
  --name appointment-mysql \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=appointment_db \
  -p 3306:3306 \
  -v mysql-data:/var/lib/mysql \
  mysql:8.0
```

### Run Appointment Service Container

```bash
docker run -d \
  --name appointment-service \
  -p 5001:5001 \
  -e MYSQL_HOST=host.docker.internal \
  -e MYSQL_PORT=3306 \
  -e MYSQL_USER=root \
  -e MYSQL_PASSWORD=root \
  -e MYSQL_DATABASE=appointment_db \
  -e JWT_SECRET_KEY=your-secret-key-change-in-production \
  --link appointment-mysql:mysql \
  appointment-service:latest
```

**Note:** For Linux, replace `host.docker.internal` with the MySQL container IP or use `--link` option.

## Verify Deployment

### Check Container Status

```bash
# List all containers
docker ps

# Check specific container
docker ps -f name=appointment-service
docker ps -f name=appointment-mysql
```

### Check Logs

```bash
# View appointment service logs
docker logs appointment-service

# Follow logs in real-time
docker logs -f appointment-service

# View MySQL logs
docker logs appointment-mysql
```

### Test Health Endpoint

```bash
# Test health endpoint
curl http://localhost:5001/health

# Expected response:
# {
#   "status": "healthy",
#   "service": "appointment-service",
#   ...
# }
```

### Test API Endpoints

```bash
# Register a user
curl -X POST http://localhost:5001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "test123",
    "role": "user"
  }'

# Login
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

## Environment Variables

You can customize the deployment using environment variables in `docker-compose.yml`:

| Variable | Description | Default |
|----------|-------------|---------|
| `MYSQL_HOST` | MySQL hostname | `mysql` |
| `MYSQL_PORT` | MySQL port | `3306` |
| `MYSQL_USER` | MySQL username | `root` |
| `MYSQL_PASSWORD` | MySQL password | `root` |
| `MYSQL_DATABASE` | Database name | `appointment_db` |
| `JWT_SECRET_KEY` | JWT secret key | `your-secret-key-change-in-production` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration (minutes) | `1440` |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiration (days) | `30` |
| `DOCTOR_SERVICE_URL` | Doctor service URL | `http://doctor-service:5001` |
| `PATIENT_SERVICE_URL` | Patient service URL | `http://patient-service:5000` |

## Troubleshooting

### Container Not Starting

```bash
# Check container status
docker ps -a

# Check logs
docker logs appointment-service

# Check if MySQL is ready
docker logs appointment-mysql
```

### Database Connection Issues

```bash
# Test MySQL connection from host
docker exec -it appointment-mysql mysql -u root -proot -e "SHOW DATABASES;"

# Test from appointment service container
docker exec -it appointment-service python -c "import pymysql; pymysql.connect(host='mysql', user='root', password='root', database='appointment_db')"
```

### Port Already in Use

```bash
# Check what's using port 5001
# Windows
netstat -ano | findstr :5001

# Linux/Mac
lsof -i :5001

# Change port in docker-compose.yml
ports:
  - "5002:5001"  # Use port 5002 on host
```

### Rebuild After Code Changes

```bash
# Rebuild and restart
docker-compose up --build -d

# Or rebuild specific service
docker-compose build appointment-service
docker-compose up -d appointment-service
```

### Access Container Shell

```bash
# Access appointment service container
docker exec -it appointment-service bash

# Access MySQL container
docker exec -it appointment-mysql bash

# Run MySQL client
docker exec -it appointment-mysql mysql -u root -proot
```

### View Resource Usage

```bash
# View container resource usage
docker stats appointment-service appointment-mysql
```

## Data Persistence

Data is persisted using Docker volumes:

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect scalable_assignment_mysql-data

# Remove volume (deletes database data)
docker volume rm scalable_assignment_mysql-data
```

## Production Considerations

1. **Change Default Passwords**: Update MySQL root password and JWT secret key
2. **Use Environment Files**: Create `.env` file for sensitive data
3. **Enable SSL/TLS**: Configure SSL for MySQL connections
4. **Resource Limits**: Add resource limits in docker-compose.yml
5. **Health Checks**: Health checks are already configured
6. **Logging**: Configure log aggregation (e.g., ELK stack)
7. **Monitoring**: Set up monitoring (e.g., Prometheus, Grafana)
8. **Backup**: Implement regular database backups

## Docker Compose Configuration

The `docker-compose.yml` file includes:

- **MySQL Service**: Database with health checks
- **Appointment Service**: Application with dependency on MySQL
- **Networks**: Isolated network for services
- **Volumes**: Persistent storage for MySQL data
- **Health Checks**: Automatic health monitoring

## Next Steps

- Import Postman collection to test API endpoints
- Configure external services (Doctor, Patient services)
- Set up CI/CD pipeline for automated deployments
- Configure monitoring and alerting

