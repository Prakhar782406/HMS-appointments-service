# Authentication Guide - JWT Authentication

## Overview

The Appointment Service uses JWT (JSON Web Tokens) for authentication. All appointment endpoints require a valid JWT token in the Authorization header.

## Architecture

- **ORM**: SQLAlchemy (Python's equivalent to Sequelize)
- **Authentication**: JWT (JSON Web Tokens)
- **Password Hashing**: SHA-256 with salt
- **Token Types**: Access tokens (24 hours) and Refresh tokens (30 days)

## Authentication Endpoints

### 1. Register User
```
POST /api/auth/register
```

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password123",
  "role": "user"
}
```

**Response (201):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": "user-uuid",
    "username": "john_doe",
    "email": "john@example.com",
    "role": "user",
    "is_active": true,
    "created_at": "2024-01-10T12:00:00",
    "updated_at": "2024-01-10T12:00:00",
    "last_login": null
  }
}
```

### 2. Login / Get Token
```
POST /api/auth/login
POST /api/auth/token
```

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "secure_password123"
}
```

**Response (200):**
```json
{
  "message": "Login successful",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 1440,
  "user": {
    "id": "user-uuid",
    "username": "john_doe",
    "email": "john@example.com",
    "role": "user",
    "is_active": true
  }
}
```

### 3. Get Current User
```
GET /api/auth/me
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "user-uuid",
  "username": "john_doe",
  "email": "john@example.com",
  "role": "user",
  "is_active": true,
  "created_at": "2024-01-10T12:00:00",
  "updated_at": "2024-01-10T12:00:00",
  "last_login": "2024-01-10T14:30:00"
}
```

## Using JWT Tokens

### Adding Token to Requests

Include the JWT token in the Authorization header:

```
Authorization: Bearer <your_access_token>
```

### Example with curl

```bash
# Login and get token
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'

# Use token to access protected endpoint
curl -X GET http://localhost:5001/api/v1/appointments/patient/patient-123 \
  -H "Authorization: Bearer <your_access_token>"
```

### Example with Python requests

```python
import requests

# Login
response = requests.post('http://localhost:5001/api/auth/login', json={
    'username': 'admin',
    'password': 'admin123'
})
token = response.json()['access_token']

# Use token
headers = {'Authorization': f'Bearer {token}'}
response = requests.get(
    'http://localhost:5001/api/v1/appointments/patient/patient-123',
    headers=headers
)
```

## User Roles

- **user**: Standard user (default)
- **admin**: Administrator with full access
- **doctor**: Doctor role
- **patient**: Patient role

## Default Users

### Admin User
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: `admin`
- **Email**: `admin@hospital.com`

This user is automatically created on first run.

## Token Expiration

- **Access Token**: 24 hours (1440 minutes)
- **Refresh Token**: 30 days

## Security Best Practices

1. **Never expose JWT secret key** in production
2. **Use HTTPS** in production to protect tokens in transit
3. **Store tokens securely** (not in localStorage for web apps)
4. **Rotate tokens** regularly
5. **Validate tokens** on every request
6. **Use strong passwords** for user accounts

## Environment Variables

Set the following environment variables for JWT configuration:

```bash
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30
```

## Error Responses

### 401 Unauthorized
```json
{
  "error": "Token is missing"
}
```

### 401 Unauthorized (Expired Token)
```json
{
  "error": "Token has expired"
}
```

### 401 Unauthorized (Invalid Token)
```json
{
  "error": "Invalid token"
}
```

### 401 Unauthorized (Invalid Credentials)
```json
{
  "error": "Invalid credentials"
}
```

## Protected Endpoints

All appointment endpoints require authentication:

- `POST /api/v1/appointments` - Book appointment
- `GET /api/v1/appointments/{id}` - Get appointment
- `POST /api/v1/appointments/{id}/reschedule` - Reschedule appointment
- `POST /api/v1/appointments/{id}/cancel` - Cancel appointment
- `POST /api/v1/appointments/{id}/confirm` - Confirm appointment
- `POST /api/v1/appointments/{id}/complete` - Complete appointment
- `GET /api/v1/appointments/patient/{patient_id}` - Get patient appointments
- `GET /api/v1/appointments/doctor/{doctor_id}` - Get doctor appointments

## Public Endpoints

These endpoints do not require authentication:

- `GET /health` - Health check
- `GET /ready` - Readiness check
- `GET /live` - Liveness check
- `POST /api/auth/register` - Register user
- `POST /api/auth/login` - Login
- `POST /api/auth/token` - Get token

## Testing Authentication

### 1. Register a new user
```bash
curl -X POST http://localhost:5001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "test123",
    "role": "user"
  }'
```

### 2. Login and get token
```bash
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "test123"
  }'
```

### 3. Use token to access protected endpoint
```bash
TOKEN="your_access_token_here"

curl -X GET http://localhost:5001/api/v1/appointments/patient/patient-123 \
  -H "Authorization: Bearer $TOKEN"
```

## Troubleshooting

### Token not working
1. Check if token is correctly formatted in Authorization header
2. Verify token hasn't expired
3. Ensure JWT_SECRET_KEY matches between token generation and validation

### Authentication errors
1. Verify username and password are correct
2. Check if user account is active
3. Ensure proper Content-Type header (application/json)

### Database issues
1. Verify database connection
2. Check if users table exists
3. Ensure default admin user was created


