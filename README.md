# Appointment Service

A microservice for managing medical appointments with booking, rescheduling, and cancellation capabilities. This service implements comprehensive business rules for slot collision detection, doctor availability checks, clinic hours validation, and lead time requirements.

## Architecture

- **Framework**: Flask (Python)
- **ORM**: SQLAlchemy (Python's equivalent to Sequelize)
- **Database**: MySQL 8.0+
- **Authentication**: JWT (JSON Web Tokens)
- **Architecture Pattern**: MVC (Model-View-Controller)

## Features

- **JWT Authentication**: Secure token-based authentication
- **User Management**: User registration and authentication
- **Book Appointments**: Create new appointments with comprehensive validation
- **Reschedule Appointments**: Update appointment date and time with business rule enforcement
- **Cancel Appointments**: Cancel appointments
- **Slot Collision Detection**: Prevents double-booking for doctors and patients
- **Doctor Availability**: Validates doctor existence, active status, and department
- **Patient Validation**: Validates patient existence and active status
- **Clinic Hours Validation**: Ensures appointments are within clinic operating hours (9 AM - 5 PM)
- **Lead Time Validation**: Requires appointments to be at least 2 hours in the future
- **Reschedule Limits**: Enforces maximum 2 reschedules per appointment
- **Reschedule Cut-off**: Prevents rescheduling within 1 hour of appointment start
- **Status Management**: Track appointment status (SCHEDULED, CONFIRMED, COMPLETED, CANCELLED, NO_SHOW)
- **Health Checks**: Comprehensive health, readiness, and liveness endpoints

## Business Rules

### Book Appointment
1. **Patient Validation**: Patient must exist and be active
2. **Doctor Validation**: Doctor must exist, be active, and belong to the requested department
3. **Clinic Hours**: Slot must be within clinic hours (9:00 AM - 5:00 PM)
4. **Lead Time**: Appointment must be at least 2 hours from current time
5. **No Overlap**: No overlapping appointments for the same doctor
6. **Patient Overlap**: No overlapping appointments for the same patient
7. **Status**: Appointment is created with status `SCHEDULED`

### Reschedule Appointment
1. **Reschedule Limit**: Maximum 2 reschedules per appointment
2. **Cut-off Time**: Cannot reschedule within 1 hour of appointment start time
3. **Validation**: All booking validations apply (clinic hours, lead time, availability)
4. **Version Control**: Appointment version is incremented on each reschedule
5. **Status Reset**: Appointment status is reset to `SCHEDULED` after reschedule

### Cancel Appointment
1. **Status Update**: Appointment status is set to `CANCELLED`
2. **Slot Release**: Cancelled appointment releases the time slot

## Architecture

### Database Schema (ER Diagram)

```
┌─────────────────────────────────────────┐
│         Appointment                     │
├─────────────────────────────────────────┤
│ PK id: VARCHAR(36)                      │
│    patient_id: VARCHAR(36) (FK)         │
│    doctor_id: VARCHAR(36) (FK)          │
│    department_id: VARCHAR(36)           │
│    appointment_date: DATETIME           │
│    duration_minutes: INT                │
│    status: VARCHAR(20)                  │
│    reschedule_count: INT                │
│    version: INT                         │
│    reason: TEXT                         │
│    notes: TEXT                          │
│    created_at: DATETIME                 │
│    updated_at: DATETIME                 │
│    cancelled_at: DATETIME (nullable)    │
└─────────────────────────────────────────┘
```

### Status Transitions

```
SCHEDULED → CONFIRMED → COMPLETED
    ↓
CANCELLED
    ↓
NO_SHOW
```

## Setup and Installation

### Prerequisites

- Python 3.11+
- MySQL 8.0+
- Docker and Docker Compose (for containerized deployment)
- Postman (for API testing)

### Local Development Setup

#### 1. Install MySQL

**Windows:**
- Download and install MySQL from [mysql.com](https://dev.mysql.com/downloads/installer/)
- Or use Chocolatey: `choco install mysql`

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql
```

**macOS:**
```bash
brew install mysql
brew services start mysql
```

#### 2. Create Database

```bash
mysql -u root -p
```

```sql
CREATE DATABASE appointment_db;
EXIT;
```

#### 3. Install Python Dependencies

```bash
cd appointment-service
pip install -r requirements.txt
```

#### 4. Configure Environment Variables

Create a `.env` file in the `appointment-service` directory (optional, defaults are provided):

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DATABASE=appointment_db
DOCTOR_SERVICE_URL=http://localhost:5001
PATIENT_SERVICE_URL=http://localhost:5000
```

#### 5. Run the Service

```bash
python app.py
```

The service will start on `http://localhost:5001`

### Docker Deployment

#### 1. Build and Run with Docker Compose

```bash
docker-compose up --build
```

#### 2. Run in Detached Mode

```bash
docker-compose up -d
```

#### 3. View Logs

```bash
docker-compose logs -f appointment-service
```

#### 4. Stop the Service

```bash
docker-compose down
```

#### 5. Stop and Remove Volumes

```bash
docker-compose down -v
```

## API Endpoints

### Base URL
- Local: `http://localhost:5001`
- Docker: `http://localhost:5001`

### Authentication Endpoints

#### Register User
```
POST /api/auth/register
```

#### Login / Get Token
```
POST /api/auth/login
POST /api/auth/token
```

#### Get Current User
```
GET /api/auth/me
Authorization: Bearer <token>
```

### Health Check Endpoints

#### Health Check
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "appointment-service",
  "timestamp": "2024-01-10T12:00:00",
  "version": "1.0.0",
  "checks": {
    "database": {
      "status": "healthy",
      "message": "Database connection successful"
    },
    "database_tables": {
      "status": "healthy",
      "message": "Database tables accessible"
    },
    "python_version": {
      "status": "healthy",
      "message": "3.11.0"
    }
  }
}
```

#### Readiness Check
```
GET /ready
```

#### Liveness Check
```
GET /live
```

### Book Appointment
```
POST /v1/appointments
```

**Request Body:**
```json
{
  "patient_id": "patient-123",
  "doctor_id": "doctor-456",
  "department_id": "dept-789",
  "appointment_date": "2024-01-15T14:00:00Z",
  "duration_minutes": 30,
  "reason": "Regular checkup",
  "notes": "First visit"
}
```

**Response (201 Created):**
```json
{
  "message": "Appointment booked successfully",
  "appointment": {
    "id": "appointment-uuid",
    "patient_id": "patient-123",
    "doctor_id": "doctor-456",
    "department_id": "dept-789",
    "appointment_date": "2024-01-15T14:00:00",
    "duration_minutes": 30,
    "status": "SCHEDULED",
    "reschedule_count": 0,
    "version": 1,
    "reason": "Regular checkup",
    "notes": "First visit",
    "created_at": "2024-01-10T12:00:00",
    "updated_at": "2024-01-10T12:00:00",
    "cancelled_at": null
  }
}
```

### Get Appointment
```
GET /v1/appointments/{appointment_id}
```

### Reschedule Appointment
```
POST /v1/appointments/{appointment_id}/reschedule
```

**Request Body:**
```json
{
  "appointment_date": "2024-01-16T15:00:00Z",
  "duration_minutes": 45,
  "reason": "Need more time"
}
```

**Response (200 OK):**
```json
{
  "message": "Appointment rescheduled successfully",
  "appointment": {
    "id": "appointment-uuid",
    "reschedule_count": 1,
    "version": 2,
    "status": "SCHEDULED",
    ...
  }
}
```

### Cancel Appointment
```
POST /v1/appointments/{appointment_id}/cancel
```

**Request Body:**
```json
{
  "reason": "Patient request"
}
```

### Confirm Appointment
```
POST /v1/appointments/{appointment_id}/confirm
```

### Complete Appointment
```
POST /v1/appointments/{appointment_id}/complete
```

### Get Appointments by Patient
```
GET /v1/appointments/patient/{patient_id}?status=SCHEDULED
```

### Get Appointments by Doctor
```
GET /v1/appointments/doctor/{doctor_id}?status=CONFIRMED&start_date=2024-01-01&end_date=2024-01-31
```

## Postman Testing Guide

### Setup Postman Collection

1. **Create a New Collection**: Name it "Appointment Service"

2. **Set Collection Variables**:
   - `base_url`: `http://localhost:5001`
   - `appointment_id`: (will be set dynamically)

### Test Cases

#### 1. Health Check
- **Method**: GET
- **URL**: `{{base_url}}/health`
- **Expected**: 200 OK with health status

#### 2. Book Appointment (Valid)
- **Method**: POST
- **URL**: `{{base_url}}/v1/appointments`
- **Headers**: `Content-Type: application/json`
- **Body**:
```json
{
  "patient_id": "patient-123",
  "doctor_id": "doctor-456",
  "department_id": "dept-789",
  "appointment_date": "2024-12-20T14:00:00Z",
  "duration_minutes": 30,
  "reason": "Regular checkup"
}
```
- **Expected**: 201 Created
- **Save**: Extract `appointment.id` to `appointment_id` variable

#### 3. Book Appointment (Invalid - Past Date)
- **Method**: POST
- **URL**: `{{base_url}}/v1/appointments`
- **Body**:
```json
{
  "patient_id": "patient-123",
  "doctor_id": "doctor-456",
  "appointment_date": "2024-01-01T10:00:00Z"
}
```
- **Expected**: 400 Bad Request (lead time validation)

#### 4. Book Appointment (Invalid - Outside Clinic Hours)
- **Method**: POST
- **URL**: `{{base_url}}/v1/appointments`
- **Body**:
```json
{
  "patient_id": "patient-123",
  "doctor_id": "doctor-456",
  "appointment_date": "2024-12-20T08:00:00Z"
}
```
- **Expected**: 400 Bad Request (clinic hours validation)

#### 5. Book Appointment (Invalid - Less than 2 hours)
- **Method**: POST
- **URL**: `{{base_url}}/v1/appointments`
- **Body**:
```json
{
  "patient_id": "patient-123",
  "doctor_id": "doctor-456",
  "appointment_date": "2024-12-10T13:00:00Z"
}
```
- **Expected**: 400 Bad Request (lead time validation)

#### 6. Get Appointment
- **Method**: GET
- **URL**: `{{base_url}}/v1/appointments/{{appointment_id}}`
- **Expected**: 200 OK

#### 7. Reschedule Appointment (Valid)
- **Method**: POST
- **URL**: `{{base_url}}/v1/appointments/{{appointment_id}}/reschedule`
- **Body**:
```json
{
  "appointment_date": "2024-12-21T15:00:00Z",
  "duration_minutes": 45
}
```
- **Expected**: 200 OK
- **Note**: Check `reschedule_count` is incremented

#### 8. Reschedule Appointment (Invalid - Max Limit)
- **Method**: POST
- **URL**: `{{base_url}}/v1/appointments/{{appointment_id}}/reschedule`
- **Body**:
```json
{
  "appointment_date": "2024-12-22T16:00:00Z"
}
```
- **Expected**: 400 Bad Request (after 2 reschedules)

#### 9. Confirm Appointment
- **Method**: POST
- **URL**: `{{base_url}}/v1/appointments/{{appointment_id}}/confirm`
- **Expected**: 200 OK
- **Note**: Status should change to `CONFIRMED`

#### 10. Cancel Appointment
- **Method**: POST
- **URL**: `{{base_url}}/v1/appointments/{{appointment_id}}/cancel`
- **Body**:
```json
{
  "reason": "Patient request"
}
```
- **Expected**: 200 OK
- **Note**: Status should change to `CANCELLED`

#### 11. Get Appointments by Patient
- **Method**: GET
- **URL**: `{{base_url}}/v1/appointments/patient/patient-123?status=SCHEDULED`
- **Expected**: 200 OK with array of appointments

#### 12. Get Appointments by Doctor
- **Method**: GET
- **URL**: `{{base_url}}/v1/appointments/doctor/doctor-456`
- **Expected**: 200 OK with array of appointments

### Postman Collection JSON

You can import this collection into Postman:

```json
{
  "info": {
    "name": "Appointment Service",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:5001"
    },
    {
      "key": "appointment_id",
      "value": ""
    }
  ],
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/health"
      }
    },
    {
      "name": "Book Appointment",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"patient_id\": \"patient-123\",\n  \"doctor_id\": \"doctor-456\",\n  \"department_id\": \"dept-789\",\n  \"appointment_date\": \"2024-12-20T14:00:00Z\",\n  \"duration_minutes\": 30,\n  \"reason\": \"Regular checkup\"\n}"
        },
        "url": "{{base_url}}/v1/appointments"
      }
    }
  ]
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Appointment must be at least 2 hours from now"
}
```

### 404 Not Found
```json
{
  "error": "Appointment not found"
}
```

### 409 Conflict
```json
{
  "error": "Doctor is not available at this time slot (slot collision)"
}
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MYSQL_HOST` | MySQL host | `localhost` |
| `MYSQL_PORT` | MySQL port | `3306` |
| `MYSQL_USER` | MySQL username | `root` |
| `MYSQL_PASSWORD` | MySQL password | `root` |
| `MYSQL_DATABASE` | MySQL database name | `appointment_db` |
| `JWT_SECRET_KEY` | JWT secret key for token signing | `your-secret-key-change-in-production` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiration (minutes) | `1440` (24 hours) |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiration (days) | `30` |
| `DOCTOR_SERVICE_URL` | Doctor Service API URL | `http://doctor-service:5001` |
| `PATIENT_SERVICE_URL` | Patient Service API URL | `http://patient-service:5000` |

## Testing

### Manual Testing with curl

**Health Check:**
```bash
curl http://localhost:5001/health
```

**Book Appointment:**
```bash
curl -X POST http://localhost:5001/v1/appointments \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "patient-123",
    "doctor_id": "doctor-456",
    "department_id": "dept-789",
    "appointment_date": "2024-12-20T14:00:00Z",
    "duration_minutes": 30,
    "reason": "Regular checkup"
  }'
```

**Reschedule Appointment:**
```bash
curl -X POST http://localhost:5001/v1/appointments/{appointment_id}/reschedule \
  -H "Content-Type: application/json" \
  -d '{
    "appointment_date": "2024-12-21T15:00:00Z",
    "duration_minutes": 45
  }'
```

**Cancel Appointment:**
```bash
curl -X POST http://localhost:5001/v1/appointments/{appointment_id}/cancel \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Patient request"
  }'
```

## Kubernetes Deployment

See `kubernetes/appointment-service-deployment.yaml` for Kubernetes manifests.

## Notes

- The service gracefully handles cases where external services (Doctor, Patient) are unavailable during development
- All timestamps are in UTC
- Appointment dates should be provided in ISO 8601 format with timezone
- The service uses optimistic locking via version field to handle concurrent updates

## License

This project is created for educational purposes as part of a college assignment.
