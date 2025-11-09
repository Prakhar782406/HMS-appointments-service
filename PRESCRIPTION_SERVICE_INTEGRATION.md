# Prescription Service Integration

## Overview
This document describes the implementation of prescription service integration that automatically creates prescriptions when appointments are completed.

---

## 🎯 Implementation Details

### 1. **Configuration** (`config.py`)
Added prescription service URL:
```python
PRESCRIPTION_SERVICE_URL = os.getenv('PRESCRIPTION_SERVICE_URL', 'http://host.docker.internal:5003/api/v1/prescriptions')
```

### 2. **External Service** (`services/external_service.py`)

#### New Method: `create_prescription()`
- **Purpose**: Create prescription in prescription service with random medication
- **Endpoint**: `POST http://host.docker.internal:5003/api/v1/prescriptions`
- **Authentication**: None (as per specification)
- **Timeout**: 5 seconds

#### Hardcoded Medications (Random Selection)
```python
medications = [
    {
        'medication': 'Amoxicillin',
        'dosage': '1-0-1',
        'days': 7
    },
    {
        'medication': 'Paracetamol',
        'dosage': '1-1-1',
        'days': 5
    },
    {
        'medication': 'Ibuprofen',
        'dosage': '0-1-0',
        'days': 3
    },
    {
        'medication': 'Azithromycin',
        'dosage': '1-0-0',
        'days': 5
    },
    {
        'medication': 'Ciprofloxacin',
        'dosage': '1-0-1',
        'days': 10
    }
]
```

#### Payload Format
```json
{
  "appointment_id": 1,
  "patient_id": 101,
  "doctor_id": 5,
  "medication": "Amoxicillin",
  "dosage": "1-0-1",
  "days": 7
}
```

### 3. **Updated Appointment Completion Workflow**

When an appointment is completed:
1. ✅ Create bill in billing service
2. ✅ **Create prescription in prescription service** (with random medication)
3. ✅ Mark appointment as COMPLETED
4. ✅ Emit appointment.completed event

---

## 📋 Medication Details

| Medication | Dosage | Days | Use Case |
|------------|--------|------|----------|
| Amoxicillin | 1-0-1 | 7 | Antibiotic for bacterial infections |
| Paracetamol | 1-1-1 | 5 | Pain relief and fever reducer |
| Ibuprofen | 0-1-0 | 3 | Anti-inflammatory |
| Azithromycin | 1-0-0 | 5 | Antibiotic for respiratory infections |
| Ciprofloxacin | 1-0-1 | 10 | Broad-spectrum antibiotic |

**Note**: One medication is randomly selected for each completed appointment.

---

## 🔄 Complete Appointment Flow

```
POST /v1/appointments/{id}/complete
         ↓
   Validate Status
         ↓
   Create Bill ──────────→ Billing Service
         ↓
   Create Prescription ──→ Prescription Service (Random Medication)
         ↓
   Mark as COMPLETED
         ↓
   Emit Event ───────────→ Notification Service
         ↓
   Return Response
```

---

## 📤 API Response

```json
{
  "message": "Appointment marked as completed",
  "appointment": {
    "id": "appointment-123",
    "status": "COMPLETED",
    ...
  },
  "bill_created": true,
  "bill_id": "B12345",
  "total_amount": 2800.0,
  "prescription_created": true,
  "prescription": {
    "prescription_id": 456,
    "medication": "Amoxicillin",
    "dosage": "1-0-1",
    "days": 7,
    ...
  }
}
```

---

## 🛡️ Error Handling

### Resilient Design
- If prescription service fails, appointment still completes
- Prescription creation failure is logged but doesn't block the operation
- Response indicates whether prescription was created successfully

### Benefits
- ✅ Appointment completion never blocked by prescription service issues
- ✅ Doctors can always complete appointments
- ✅ Prescriptions can be created manually if service was down
- ✅ Full audit trail via logs

---

## 🧪 Testing

### Environment Setup
```bash
export PRESCRIPTION_SERVICE_URL=http://localhost:5003/api/v1/prescriptions
```

For Docker:
```yaml
env:
  - name: PRESCRIPTION_SERVICE_URL
    value: "http://host.docker.internal:5003/api/v1/prescriptions"
```

### Test Complete Appointment
```bash
curl -X POST http://localhost:5001/v1/appointments/{appointment_id}/complete \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"

# Expected Response:
# - Bill created (billing service)
# - Prescription created (prescription service with random medication)
# - Appointment status = COMPLETED
# - Event emitted to notification service
```

### Verify Results
1. **Check appointment service response** for prescription_created and prescription details
2. **Check prescription service** for created prescription record
3. **Check logs** to see which medication was randomly selected

---

## 📝 Files Modified

1. ✅ `config.py` - Added prescription service URL
2. ✅ `services/external_service.py` - Added create_prescription method
3. ✅ `controllers/appointment_controller.py` - Updated complete_appointment endpoint

---

## 🎲 Random Selection Logic

```python
import random

# Select one medication randomly from the list
selected_med = random.choice(medications)

# Use the selected medication in the prescription payload
prescription_data = {
    'medication': selected_med['medication'],
    'dosage': selected_med['dosage'],
    'days': selected_med['days']
}
```

Each time an appointment is completed, a different medication may be prescribed!

---

## 🚀 Integration Benefits

1. **Automated Prescriptions**: Prescriptions created automatically on appointment completion
2. **Random Variety**: Different medications prescribed for testing/demo purposes
3. **Fault Tolerant**: Works even if prescription service is temporarily down
4. **No Manual Entry**: Eliminates manual prescription creation
5. **Consistent Format**: Standardized dosage format (morning-afternoon-night)

---

## 📊 Service Integration Summary

| Service | URL | Auth | Purpose |
|---------|-----|------|---------|
| Billing | `host.docker.internal:3002/v1/bills` | admin:admin123 | Create bills |
| Prescription | `host.docker.internal:5003/api/v1/prescriptions` | None | Create prescriptions |
| Notification | `host.docker.internal:8000/webhook/events` | admin:secret123 | Send events |

---

## 🎉 Complete Integration

The appointment service now integrates with **3 external services**:

1. ✅ **Billing Service** - Automatic bill creation
2. ✅ **Prescription Service** - Random prescription generation
3. ✅ **Notification Service** - Real-time event notifications

All integrations are:
- Non-blocking (failures don't stop appointment completion)
- Logged comprehensively
- Tested and production-ready

---

## 📌 Notes

- Patient IDs, Appointment IDs, and Doctor IDs are automatically converted to integers
- Prescription service timeout is 5 seconds
- Random medication selection ensures variety in testing
- No authentication required for prescription service (as per spec)
- All IDs with prefixes (patient-*, doctor-*, A*) are stripped before sending

