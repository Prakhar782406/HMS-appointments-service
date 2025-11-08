# Quick Start Guide - Appointment Service

## Prerequisites
- Python 3.11+
- MySQL 8.0+
- Docker (optional, for containerized setup)

## Local Setup (5 minutes)

### 1. Setup MySQL Database

**Windows:**
```bash
setup_mysql.bat
```

**Linux/macOS:**
```bash
chmod +x setup_mysql.sh
./setup_mysql.sh
```

**Or manually:**
```bash
mysql -u root -p
```

```sql
CREATE DATABASE appointment_db;
EXIT;
```

### 2. Install Dependencies

```bash
cd appointment-service
pip install -r requirements.txt
```

### 3. Run the Service

```bash
python app.py
```

Service will start on `http://localhost:5001`

### 4. Test the Service

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

## Docker Setup (3 minutes)

### 1. Start Services

```bash
docker-compose up --build
```

### 2. Verify Services

```bash
# Check if MySQL is running
docker-compose ps

# Check service logs
docker-compose logs appointment-service

# Health check
curl http://localhost:5001/health
```

### 3. Stop Services

```bash
docker-compose down
```

## Postman Testing

1. **Import Collection**: Import `POSTMAN_COLLECTION.json` into Postman
2. **Set Variables**: Update `base_url` if needed (default: `http://localhost:5001`)
3. **Run Tests**: Execute requests in order:
   - Health Check
   - Book Appointment (Valid)
   - Get Appointment
   - Reschedule Appointment
   - Confirm Appointment
   - Cancel Appointment

## Common Issues

### MySQL Connection Error
- **Issue**: `Can't connect to MySQL server`
- **Solution**: 
  - Ensure MySQL is running: `mysql -u root -p`
  - Check credentials in environment variables
  - Verify database exists: `SHOW DATABASES;`

### Port Already in Use
- **Issue**: `Address already in use`
- **Solution**: 
  - Change port in `app.py` or use environment variable
  - Kill process using port: `lsof -ti:5001 | xargs kill` (Linux/macOS)

### Database Table Not Found
- **Issue**: `Table 'appointments' doesn't exist`
- **Solution**: 
  - Tables are created automatically on first run
  - Check database connection
  - Verify user has CREATE TABLE permissions

## API Endpoints Quick Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/v1/appointments` | POST | Book appointment |
| `/v1/appointments/{id}` | GET | Get appointment |
| `/v1/appointments/{id}/reschedule` | POST | Reschedule appointment |
| `/v1/appointments/{id}/cancel` | POST | Cancel appointment |
| `/v1/appointments/{id}/confirm` | POST | Confirm appointment |
| `/v1/appointments/{id}/complete` | POST | Complete appointment |
| `/v1/appointments/patient/{id}` | GET | Get patient appointments |
| `/v1/appointments/doctor/{id}` | GET | Get doctor appointments |

## Business Rules Summary

1. **Booking**: 
   - Minimum 2 hours lead time
   - Clinic hours: 9 AM - 5 PM UTC
   - No overlapping appointments
   - Patient and doctor must be active

2. **Rescheduling**: 
   - Maximum 2 reschedules
   - Cannot reschedule within 1 hour of appointment

3. **Cancellation**: 
   - Releases time slot

## Need Help?

- Check the full [README.md](README.md) for detailed documentation
- Review API examples in `POSTMAN_COLLECTION.json`
- Run integration tests: `python test_appointment.py`


