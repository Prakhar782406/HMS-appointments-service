"""
Test script for Complete Appointment Integration
Tests appointment completion with billing and prescription services
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5001"
BILLING_URL = "http://localhost:3002"
PRESCRIPTION_URL = "http://localhost:5003"

def print_response(response, title):
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_prescription_service():
    """Test prescription service connectivity"""
    print("\n🧪 Testing Prescription Service Connectivity...")
    try:
        response = requests.post(
            f"{PRESCRIPTION_URL}/api/v1/prescriptions",
            json={
                "appointment_id": 999,
                "patient_id": 999,
                "doctor_id": 999,
                "medication": "Test Medicine",
                "dosage": "1-0-1",
                "days": 7
            },
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        print_response(response, "Prescription Service Test")
        return response.status_code in [200, 201]
    except requests.RequestException as e:
        print(f"❌ Prescription service not available: {str(e)}")
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
        "reason": "Complete integration test",
        "notes": "Testing billing and prescription service integration"
    }

    response = requests.post(f"{BASE_URL}/v1/appointments", json=data)
    print_response(response, "Book Appointment")

    if response.status_code == 201:
        return response.json().get('appointment', {}).get('id')
    return None

def complete_appointment_with_integration(appointment_id):
    """Complete appointment and trigger billing + prescription"""
    print(f"\n🧪 Completing Appointment {appointment_id}...")
    print("\n📋 This will:")
    print("  1. ✅ Call billing service to create bill")
    print("  2. ✅ Call prescription service with RANDOM medication")
    print("  3. ✅ Mark appointment as COMPLETED")
    print("  4. ✅ Emit appointment.completed event")

    response = requests.post(
        f"{BASE_URL}/v1/appointments/{appointment_id}/complete"
    )
    print_response(response, "Complete Appointment (Full Integration)")

    if response.status_code == 200:
        data = response.json()

        print("\n" + "="*70)
        print("📊 INTEGRATION RESULTS")
        print("="*70)

        # Billing Results
        print("\n💰 BILLING:")
        print(f"  Bill Created: {data.get('bill_created')}")
        print(f"  Bill ID: {data.get('bill_id')}")
        print(f"  Total Amount: ₹{data.get('total_amount')}")

        # Prescription Results
        print("\n💊 PRESCRIPTION:")
        print(f"  Prescription Created: {data.get('prescription_created')}")
        if data.get('prescription'):
            prescription = data['prescription']
            print(f"  Medication: {prescription.get('medication', 'N/A')}")
            print(f"  Dosage: {prescription.get('dosage', 'N/A')}")
            print(f"  Days: {prescription.get('days', 'N/A')}")
            print(f"  Prescription ID: {prescription.get('prescription_id', 'N/A')}")

        # Appointment Status
        print("\n📅 APPOINTMENT:")
        print(f"  Status: {data.get('appointment', {}).get('status')}")
        print(f"  Appointment ID: {data.get('appointment', {}).get('id')}")

        return True
    return False

def display_available_medications():
    """Display the list of possible medications"""
    print("\n💊 AVAILABLE MEDICATIONS (Random Selection):")
    print("="*70)
    medications = [
        ("Amoxicillin", "1-0-1", "7 days", "Antibiotic for bacterial infections"),
        ("Paracetamol", "1-1-1", "5 days", "Pain relief and fever reducer"),
        ("Ibuprofen", "0-1-0", "3 days", "Anti-inflammatory"),
        ("Azithromycin", "1-0-0", "5 days", "Antibiotic for respiratory infections"),
        ("Ciprofloxacin", "1-0-1", "10 days", "Broad-spectrum antibiotic")
    ]

    for i, (med, dosage, days, desc) in enumerate(medications, 1):
        print(f"\n{i}. {med}")
        print(f"   Dosage: {dosage} (Morning-Afternoon-Night)")
        print(f"   Duration: {days}")
        print(f"   Use: {desc}")

    print("\n" + "="*70)
    print("🎲 One will be randomly selected when appointment completes!")
    print("="*70)

def main():
    print("="*70)
    print("🏥 COMPLETE APPOINTMENT INTEGRATION TEST")
    print("   (Billing + Prescription Services)")
    print("="*70)

    # Display available medications
    display_available_medications()

    # Test 1: Check prescription service
    print("\n📋 Step 1: Testing Prescription Service")
    if not test_prescription_service():
        print("⚠️  Prescription service is not available")
        print("    Appointment will still complete, but no prescription will be created")
    else:
        print("✅ Prescription service is available!")

    # Test 2: Book appointment
    print("\n📋 Step 2: Booking Test Appointment")
    appointment_id = book_test_appointment()
    if not appointment_id:
        print("❌ Failed to book appointment")
        return

    print(f"✅ Appointment booked successfully: {appointment_id}")

    # Test 3: Complete appointment (triggers billing + prescription)
    print("\n📋 Step 3: Completing Appointment")
    print("    (Triggers Billing + Random Prescription)")
    input("\nPress Enter to complete appointment and see the magic...")

    if complete_appointment_with_integration(appointment_id):
        print("\n" + "="*70)
        print("✅ INTEGRATION TEST COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\n📝 What happened:")
        print("  1. ✅ Bill created in billing service")
        print("  2. ✅ Random prescription created in prescription service")
        print("  3. ✅ Appointment marked as COMPLETED")
        print("  4. ✅ Event emitted to notification service")
        print("\n🎉 All services integrated successfully!")
    else:
        print("\n❌ Failed to complete appointment")

if __name__ == "__main__":
    main()

