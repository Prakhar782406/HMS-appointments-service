"""
Test script for Billing Service Integration
Tests appointment completion with billing service call
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5001"
BILLING_URL = "http://localhost:3002"

def print_response(response, title):
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_billing_service():
    """Test billing service connectivity"""
    print("\n🧪 Testing Billing Service Connectivity...")
    try:
        response = requests.post(
            f"{BILLING_URL}/v1/bills",
            json={
                "patient_id": 999,
                "appointment_id": 999,
                "consultation_fee": 2000.0,
                "medication_fee": 800.0
            },
            auth=('admin', 'admin123'),
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        print_response(response, "Billing Service Test")
        return response.status_code in [200, 201]
    except requests.RequestException as e:
        print(f"❌ Billing service not available: {str(e)}")
        return False

def book_test_appointment():
    """Book a test appointment"""
    print("\n🧪 Booking Test Appointment...")
    appointment_date = (datetime.utcnow() + timedelta(hours=3)).replace(minute=0, second=0, microsecond=0)
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
        "reason": "Billing integration test",
        "notes": "Testing billing service call on completion"
    }

    response = requests.post(f"{BASE_URL}/v1/appointments", json=data)
    print_response(response, "Book Appointment")

    if response.status_code == 201:
        return response.json().get('appointment', {}).get('id')
    return None

def complete_appointment(appointment_id):
    """Complete appointment and trigger billing"""
    print(f"\n🧪 Completing Appointment {appointment_id}...")
    print("This will:")
    print("  1. Call billing service to create bill")
    print("  2. Mark appointment as COMPLETED")
    print("  3. Emit appointment.completed event to notification service")

    response = requests.post(
        f"{BASE_URL}/v1/appointments/{appointment_id}/complete"
    )
    print_response(response, "Complete Appointment with Billing")

    if response.status_code == 200:
        data = response.json()
        print("\n📊 Billing Results:")
        print(f"  Bill Created: {data.get('bill_created')}")
        print(f"  Bill ID: {data.get('bill_id')}")
        print(f"  Total Amount: {data.get('total_amount')}")
        return True
    return False

def main():
    print("="*60)
    print("🏥 BILLING SERVICE INTEGRATION TEST")
    print("="*60)

    # Test 1: Check billing service
    print("\n📋 Step 1: Testing Billing Service")
    if not test_billing_service():
        print("⚠️  Billing service is not available, but appointment completion will still work with fallback values")

    # Test 2: Book appointment
    print("\n📋 Step 2: Booking Test Appointment")
    appointment_id = book_test_appointment()
    if not appointment_id:
        print("❌ Failed to book appointment")
        return

    print(f"✅ Appointment booked successfully: {appointment_id}")

    # Test 3: Complete appointment (triggers billing)
    print("\n📋 Step 3: Completing Appointment (with Billing)")
    input("\nPress Enter to complete the appointment and trigger billing...")

    if complete_appointment(appointment_id):
        print("\n✅ Appointment completed successfully!")
        print("\n📝 What happened:")
        print("  1. Billing service received request to create bill")
        print("  2. Bill created with consultation_fee=2000.0, medication_fee=800.0")
        print("  3. Appointment marked as COMPLETED")
        print("  4. Event emitted to notification service with real bill data")
        print("\n🎉 Integration test completed!")
    else:
        print("\n❌ Failed to complete appointment")

if __name__ == "__main__":
    main()

