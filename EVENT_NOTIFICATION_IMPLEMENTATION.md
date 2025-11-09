# Event Notification Implementation

## Overview
This document describes the implementation of event notifications to the notification service after appointment operations (booking, rescheduling, canceling, and completing).

## Changes Made

### 1. Configuration (`config.py`)
- **Added**: `NOTIFICATION_SERVICE_URL` configuration
  - Default: `http://localhost:8000/webhook/events`
  - Can be overridden via environment variable: `NOTIFICATION_SERVICE_URL`
- **Added**: `BILLING_SERVICE_URL` configuration
  - Default: `http://host.docker.internal:3002/v1/bills`
  - Can be overridden via environment variable: `BILLING_SERVICE_URL`

```python
NOTIFICATION_SERVICE_URL = os.getenv('NOTIFICATION_SERVICE_URL', 'http://localhost:8000/webhook/events')
BILLING_SERVICE_URL = os.getenv('BILLING_SERVICE_URL', 'http://host.docker.internal:3002/v1/bills')
```

### 2. External Service (`services/external_service.py`)
- **Added**: `emit_appointment_event(event_data: Dict) -> bool` method
  - Sends POST request to notification service with event payload
  - **Uses Basic Authentication**: username=`admin`, password=`secret123`
  - Handles timeout (5 seconds)
  - Logs success/failure but doesn't fail the appointment operation
  - Returns `True` on success (status 200, 201, or 202), `False` otherwise

- **Added**: `create_bill(patient_id, appointment_id, consultation_fee, medication_fee) -> Tuple[bool, Optional[Dict]]` method
  - Sends POST request to billing service to create a bill
  - **Uses Basic Authentication**: username=`admin`, password=`admin123`
  - Default consultation_fee: 2000.0, medication_fee: 800.0
  - Returns tuple of (success, bill_data)
  - Handles timeout (5 seconds)
  - Logs success/failure but doesn't fail the appointment completion

### 3. Appointment Service (`services/appointment_service.py`)
- **Added**: `_format_datetime(dt: datetime) -> str` helper method
  - Formats datetime to ISO format with 'Z' suffix for UTC
  - Used consistently across all event payloads

#### Updated Methods:

**`book_appointment()`**
- Emits `appointment.scheduled` event after successful booking
- Event payload includes:
  - `event_type`: "appointment.scheduled"
  - `appointment_id`: The newly created appointment ID
  - `patient_id`: Patient ID
  - `doctor_id`: Doctor ID
  - `department`: Department ID
  - `slot`: Object with `start_time` and `end_time` (ISO format with Z)
  - `status`: "SCHEDULED"

**`reschedule_appointment()`**
- Emits `appointment.rescheduled` event after successful rescheduling
- Event payload includes:
  - `event_type`: "appointment.rescheduled"
  - `appointment_id`: The appointment ID
  - `old_slot`: Object with previous `start_time` and `end_time`
  - `new_slot`: Object with new `start_time` and `end_time`
  - `version`: Current version number
  - `reschedule_count`: Current reschedule count
  - `status`: "SCHEDULED"

**`cancel_appointment()`**
- Emits `appointment.cancelled` event after successful cancellation
- Event payload includes:
  - `event_type`: "appointment.cancelled"
  - `appointment_id`: The appointment ID
  - `patient_id`: Patient ID
  - `doctor_id`: Doctor ID
  - `cancelled_at`: Cancellation timestamp (ISO format with Z)
  - `policy_applied`: Default "50_percent_fee" (can be enhanced)
  - `refund_amount`: Default 500.0 (can be enhanced)
  - `status`: "CANCELLED"

### 4. Appointment Controller (`controllers/appointment_controller.py`)
- **Added**: Import for `ExternalService`

**Updated `complete_appointment()` endpoint**
- **Calls Billing Service** to create a bill before marking appointment as completed
  - Sends patient_id, appointment_id, consultation_fee (2000.0), medication_fee (800.0)
  - Uses Basic Auth: admin:admin123
- Emits `appointment.completed` event after marking appointment as completed
- Event payload includes:
  - `event_type`: "appointment.completed"
  - `appointment_id`: The appointment ID
  - `patient_id`: Patient ID
  - `doctor_id`: Doctor ID
  - `completed_at`: Completion timestamp (ISO format with Z)
  - `bill_id`: Real bill ID from billing service (or mock if service fails)
  - `total_amount`: Real total amount from billing service (or calculated if service fails)
  - `status`: "COMPLETED"
- Response includes bill creation status and bill details

## Event Payload Examples

### 1. appointment.scheduled
```json
{
  "event_type": "appointment.scheduled",
  "appointment_id": "A12345",
  "patient_id": "P1001",
  "doctor_id": "D2001",
  "department": "Cardiology",
  "slot": {
    "start_time": "2025-10-24T10:00:00Z",
    "end_time": "2025-10-24T10:30:00Z"
  },
  "status": "SCHEDULED"
}
```

### 2. appointment.rescheduled
```json
{
  "event_type": "appointment.rescheduled",
  "appointment_id": "A12345",
  "old_slot": {
    "start_time": "2025-10-24T10:00:00Z",
    "end_time": "2025-10-24T10:30:00Z"
  },
  "new_slot": {
    "start_time": "2025-10-25T11:00:00Z",
    "end_time": "2025-10-25T11:30:00Z"
  },
  "version": 2,
  "reschedule_count": 1,
  "status": "SCHEDULED"
}
```

### 3. appointment.cancelled
```json
{
  "event_type": "appointment.cancelled",
  "appointment_id": "A12345",
  "patient_id": "P1001",
  "doctor_id": "D2001",
  "cancelled_at": "2025-10-23T12:30:00Z",
  "policy_applied": "50_percent_fee",
  "refund_amount": 500.0,
  "status": "CANCELLED"
}
```

### 4. appointment.completed
```json
{
  "event_type": "appointment.completed",
  "appointment_id": "A12345",
  "patient_id": "P1001",
  "doctor_id": "D2001",
  "completed_at": "2025-10-23T11:00:00Z",
  "bill_id": "B5678",
  "total_amount": 2800.0,
  "status": "COMPLETED"
}
```
**Note**: `bill_id` and `total_amount` are fetched from the billing service.

## Testing

### Authentication
All event emissions to the notification service use **Basic Authentication**:
- **Notification Service**: username=`admin`, password=`secret123`
- **Billing Service**: username=`admin`, password=`admin123`

Ensure your services are configured to accept these credentials.

### Environment Setup
To test with local services:
```bash
export NOTIFICATION_SERVICE_URL=http://localhost:8000/webhook/events
export BILLING_SERVICE_URL=http://localhost:3002/v1/bills
```

For Docker/Kubernetes:
```yaml
env:
  - name: NOTIFICATION_SERVICE_URL
    value: "http://notification-service:8000/webhook/events"
  - name: BILLING_SERVICE_URL
    value: "http://billing-service:3002/v1/bills"
```

### Testing Endpoints

1. **Book Appointment**
   ```bash
   POST /v1/appointments
   # Check notification service logs for appointment.scheduled event
   ```

2. **Reschedule Appointment**
   ```bash
   POST /v1/appointments/{id}/reschedule
   # Check notification service logs for appointment.rescheduled event
   ```

3. **Cancel Appointment**
   ```bash
   POST /v1/appointments/{id}/cancel
   # Check notification service logs for appointment.cancelled event
   ```

4. **Complete Appointment**
   ```bash
   POST /v1/appointments/{id}/complete
   # Creates a bill in billing service with:
   #   - consultation_fee: 2000.0
   #   - medication_fee: 800.0
   #   - total: 2800.0
   # Check billing service for created bill
   # Check notification service logs for appointment.completed event
   ```

## Error Handling
- Event emission failures are logged but **do not** fail the appointment operation
- Billing service failures are logged but **do not** fail the appointment completion
  - If billing service fails, appointment still completes with fallback bill_id and total_amount
- This ensures appointment operations remain reliable even if external services are down
- All failures are logged with appropriate error messages for debugging

## Future Enhancements
1. **Dynamic policy calculation** for cancellations based on time before appointment
2. **Dynamic billing calculation** based on appointment type, duration, and services rendered
3. **Retry mechanism** for failed event emissions and billing calls (e.g., using message queue)
4. **Event versioning** for backward compatibility
5. **No-show marking** event implementation (currently not triggered automatically)
6. **Configurable fees** via environment variables or database

## Notes
- All datetime values in events use ISO 8601 format with 'Z' suffix (UTC timezone)
- Event emission is asynchronous (fire-and-forget) with a 5-second timeout
- The notification service URL can be configured via environment variable for different environments

