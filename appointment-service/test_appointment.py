"""
Integration test script for Appointment Service
Tests the complete workflow with business rules
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5001"

def print_response(response, title):
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"{'='*50}")
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print_response(response, "Health Check")
    return response.status_code == 200

def test_book_appointment_valid():
    """Test booking a valid appointment"""
    # Book appointment 3 hours from now (meets 2-hour lead time)
    appointment_date = (datetime.utcnow() + timedelta(hours=3)).replace(minute=0, second=0, microsecond=0)
    # Ensure it's within clinic hours (9 AM - 5 PM)
    if appointment_date.hour < 9:
        appointment_date = appointment_date.replace(hour=14)
    elif appointment_date.hour >= 17:
        appointment_date = appointment_date.replace(hour=14)
    
    data = {
        "patient_id": "patient-123",
        "doctor_id": "doctor-456",
        "department_id": "dept-789",
        "appointment_date": appointment_date.isoformat() + "Z",
        "duration_minutes": 30,
        "reason": "Regular checkup",
        "notes": "First visit"
    }
    
    response = requests.post(f"{BASE_URL}/v1/appointments", json=data)
    print_response(response, "Book Appointment (Valid)")
    
    if response.status_code == 201:
        return response.json().get('appointment', {}).get('id')
    return None

def test_book_appointment_lead_time():
    """Test booking with insufficient lead time"""
    # Book appointment 1 hour from now (less than 2-hour requirement)
    appointment_date = (datetime.utcnow() + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    
    data = {
        "patient_id": "patient-123",
        "doctor_id": "doctor-456",
        "appointment_date": appointment_date.isoformat() + "Z"
    }
    
    response = requests.post(f"{BASE_URL}/v1/appointments", json=data)
    print_response(response, "Book Appointment (Invalid - Lead Time)")
    return response.status_code == 400

def test_book_appointment_clinic_hours():
    """Test booking outside clinic hours"""
    # Book appointment at 8 AM (outside 9 AM - 5 PM)
    appointment_date = (datetime.utcnow() + timedelta(hours=3)).replace(hour=8, minute=0, second=0, microsecond=0)
    
    data = {
        "patient_id": "patient-123",
        "doctor_id": "doctor-456",
        "appointment_date": appointment_date.isoformat() + "Z"
    }
    
    response = requests.post(f"{BASE_URL}/v1/appointments", json=data)
    print_response(response, "Book Appointment (Invalid - Clinic Hours)")
    return response.status_code == 400

def test_get_appointment(appointment_id):
    """Test getting an appointment"""
    response = requests.get(f"{BASE_URL}/v1/appointments/{appointment_id}")
    print_response(response, "Get Appointment")
    return response.status_code == 200

def test_reschedule_appointment(appointment_id):
    """Test rescheduling an appointment"""
    # Reschedule to 4 hours from now
    new_date = (datetime.utcnow() + timedelta(hours=4)).replace(minute=0, second=0, microsecond=0)
    if new_date.hour < 9:
        new_date = new_date.replace(hour=15)
    elif new_date.hour >= 17:
        new_date = new_date.replace(hour=15)
    
    data = {
        "appointment_date": new_date.isoformat() + "Z",
        "duration_minutes": 45,
        "reason": "Need more time"
    }
    
    response = requests.post(f"{BASE_URL}/v1/appointments/{appointment_id}/reschedule", json=data)
    print_response(response, "Reschedule Appointment")
    return response.status_code == 200

def test_reschedule_limit(appointment_id):
    """Test reschedule limit (max 2 reschedules)"""
    # Try to reschedule 3 times
    for i in range(3):
        new_date = (datetime.utcnow() + timedelta(hours=5+i)).replace(minute=0, second=0, microsecond=0)
        if new_date.hour < 9:
            new_date = new_date.replace(hour=15)
        elif new_date.hour >= 17:
            new_date = new_date.replace(hour=15)
        
        data = {
            "appointment_date": new_date.isoformat() + "Z"
        }
        
        response = requests.post(f"{BASE_URL}/v1/appointments/{appointment_id}/reschedule", json=data)
        print_response(response, f"Reschedule Attempt {i+1}")
        
        if response.status_code != 200:
            # Expected to fail on 3rd attempt
            if i == 2:
                return True
            return False
    
    return False

def test_confirm_appointment(appointment_id):
    """Test confirming an appointment"""
    response = requests.post(f"{BASE_URL}/v1/appointments/{appointment_id}/confirm")
    print_response(response, "Confirm Appointment")
    return response.status_code == 200

def test_cancel_appointment(appointment_id):
    """Test cancelling an appointment"""
    data = {
        "reason": "Patient request",
        "base_amount": 100
    }
    
    response = requests.post(f"{BASE_URL}/v1/appointments/{appointment_id}/cancel", json=data)
    print_response(response, "Cancel Appointment")
    return response.status_code == 200

def test_get_appointments_by_patient(patient_id):
    """Test getting all appointments for a patient"""
    response = requests.get(f"{BASE_URL}/v1/appointments/patient/{patient_id}")
    print_response(response, "Get Appointments by Patient")
    return response.status_code == 200

def test_get_appointments_by_doctor(doctor_id):
    """Test getting all appointments for a doctor"""
    response = requests.get(f"{BASE_URL}/v1/appointments/doctor/{doctor_id}")
    print_response(response, "Get Appointments by Doctor")
    return response.status_code == 200

def test_slot_collision():
    """Test slot collision detection"""
    # Book first appointment
    appointment_date = (datetime.utcnow() + timedelta(hours=6)).replace(minute=0, second=0, microsecond=0)
    if appointment_date.hour < 9:
        appointment_date = appointment_date.replace(hour=14)
    elif appointment_date.hour >= 17:
        appointment_date = appointment_date.replace(hour=14)
    
    data1 = {
        "patient_id": "patient-789",
        "doctor_id": "doctor-456",
        "appointment_date": appointment_date.isoformat() + "Z",
        "duration_minutes": 30
    }
    
    response1 = requests.post(f"{BASE_URL}/v1/appointments", json=data1)
    print_response(response1, "Book First Appointment (for collision test)")
    
    if response1.status_code != 201:
        return False
    
    # Try to book overlapping appointment
    overlapping_date = datetime.fromisoformat(appointment_date.isoformat()) + timedelta(minutes=15)
    data2 = {
        "patient_id": "patient-999",
        "doctor_id": "doctor-456",
        "appointment_date": overlapping_date.isoformat() + "Z",
        "duration_minutes": 30
    }
    
    response2 = requests.post(f"{BASE_URL}/v1/appointments", json=data2)
    print_response(response2, "Book Overlapping Appointment (should fail)")
    
    # Should fail with 409 Conflict
    return response2.status_code == 409

def main():
    print("="*50)
    print("Appointment Service Integration Tests")
    print("="*50)
    
    # Run tests
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Health check
    tests_total += 1
    if test_health():
        tests_passed += 1
        print("✓ Health check passed")
    else:
        print("✗ Health check failed")
        return
    
    # Test 2: Book appointment (valid)
    tests_total += 1
    appointment_id = test_book_appointment_valid()
    if appointment_id:
        tests_passed += 1
        print(f"✓ Book appointment passed (ID: {appointment_id})")
    else:
        print("✗ Book appointment failed")
        return
    
    # Test 3: Book appointment (lead time validation)
    tests_total += 1
    if test_book_appointment_lead_time():
        tests_passed += 1
        print("✓ Lead time validation passed")
    else:
        print("✗ Lead time validation failed")
    
    # Test 4: Book appointment (clinic hours validation)
    tests_total += 1
    if test_book_appointment_clinic_hours():
        tests_passed += 1
        print("✓ Clinic hours validation passed")
    else:
        print("✗ Clinic hours validation failed")
    
    # Test 5: Get appointment
    tests_total += 1
    if test_get_appointment(appointment_id):
        tests_passed += 1
        print("✓ Get appointment passed")
    else:
        print("✗ Get appointment failed")
    
    # Test 6: Reschedule appointment
    tests_total += 1
    if test_reschedule_appointment(appointment_id):
        tests_passed += 1
        print("✓ Reschedule appointment passed")
    else:
        print("✗ Reschedule appointment failed")
    
    # Test 7: Reschedule limit
    tests_total += 1
    if test_reschedule_limit(appointment_id):
        tests_passed += 1
        print("✓ Reschedule limit validation passed")
    else:
        print("✗ Reschedule limit validation failed")
    
    # Test 8: Confirm appointment
    tests_total += 1
    if test_confirm_appointment(appointment_id):
        tests_passed += 1
        print("✓ Confirm appointment passed")
    else:
        print("✗ Confirm appointment failed")
    
    # Test 9: Get appointments by patient
    tests_total += 1
    if test_get_appointments_by_patient("patient-123"):
        tests_passed += 1
        print("✓ Get appointments by patient passed")
    else:
        print("✗ Get appointments by patient failed")
    
    # Test 10: Get appointments by doctor
    tests_total += 1
    if test_get_appointments_by_doctor("doctor-456"):
        tests_passed += 1
        print("✓ Get appointments by doctor passed")
    else:
        print("✗ Get appointments by doctor failed")
    
    # Test 11: Slot collision detection
    tests_total += 1
    if test_slot_collision():
        tests_passed += 1
        print("✓ Slot collision detection passed")
    else:
        print("✗ Slot collision detection failed")
    
    # Test 12: Cancel appointment (create new one first)
    tests_total += 1
    cancel_appointment_id = test_book_appointment_valid()
    if cancel_appointment_id and test_cancel_appointment(cancel_appointment_id):
        tests_passed += 1
        print("✓ Cancel appointment passed")
    else:
        print("✗ Cancel appointment failed")
    
    # Summary
    print("\n" + "="*50)
    print("Test Summary")
    print("="*50)
    print(f"Tests passed: {tests_passed}/{tests_total}")
    if tests_passed == tests_total:
        print("✓ All tests passed!")
    else:
        print(f"✗ {tests_total - tests_passed} test(s) failed")

if __name__ == "__main__":
    main()
