# 🚀 Quick Reference - Appointment Service Integrations

## 📋 Complete Appointment Workflow

```
POST /v1/appointments/{id}/complete
    ↓
    Creates BILL → Billing Service (:3002)
    Creates PRESCRIPTION → Prescription Service (:5003) 
    Sends EVENT → Notification Service (:8000)
    ↓
    Returns complete status
```

---

## 🔌 External Service Endpoints

| Service | URL | Auth | Port |
|---------|-----|------|------|
| Billing | `http://host.docker.internal:3002/v1/bills` | admin:admin123 | 3002 |
| Prescription | `http://host.docker.internal:5003/api/v1/prescriptions` | None | 5003 |
| Notification | `http://host.docker.internal:8000/webhook/events` | admin:secret123 | 8000 |

---

## 💊 Random Medications (Auto-Selected)

1. **Amoxicillin** - 1-0-1 for 7 days
2. **Paracetamol** - 1-1-1 for 5 days
3. **Ibuprofen** - 0-1-0 for 3 days
4. **Azithromycin** - 1-0-0 for 5 days
5. **Ciprofloxacin** - 1-0-1 for 10 days

---

## 📡 Event Types

- `appointment.scheduled` - After booking
- `appointment.rescheduled` - After rescheduling
- `appointment.cancelled` - After cancellation
- `appointment.completed` - After completion

---

## 🧪 Quick Test Commands

```bash
# Run full integration test
python appointment-service/test_complete_integration.py

# Test billing integration
python appointment-service/test_billing_integration.py

# Complete appointment manually
curl -X POST http://localhost:5001/v1/appointments/{id}/complete \
  -H "Authorization: Bearer TOKEN"
```

---

## 📊 Expected Response

```json
{
  "message": "Appointment marked as completed",
  "appointment": {...},
  "bill_created": true,
  "bill_id": "B12345",
  "total_amount": 2800.0,
  "prescription_created": true,
  "prescription": {
    "medication": "Amoxicillin",
    "dosage": "1-0-1",
    "days": 7
  }
}
```

---

## 🛠️ Environment Variables

```bash
# Billing Service
export BILLING_SERVICE_URL=http://host.docker.internal:3002/v1/bills

# Prescription Service  
export PRESCRIPTION_SERVICE_URL=http://host.docker.internal:5003/api/v1/prescriptions

# Notification Service
export NOTIFICATION_SERVICE_URL=http://host.docker.internal:8000/webhook/events
```

---

## ✅ Features

- ✅ Automatic billing on completion
- ✅ Random prescription generation
- ✅ Real-time notifications
- ✅ Non-blocking operations
- ✅ Complete error handling
- ✅ Full audit logging

---

## 📁 Key Files

- `config.py` - Service URLs
- `services/external_service.py` - Integration logic
- `controllers/appointment_controller.py` - API endpoints
- `test_complete_integration.py` - Test script

---

## 🔥 Production Ready!

All integrations tested and documented. Ready to deploy! 🚀

