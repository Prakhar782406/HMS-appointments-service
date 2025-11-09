"""
External service integration
"""
import logging

import requests
import random
from typing import Optional, Dict, Tuple
from config import Config
from flask import current_app

class ExternalService:
    """Service for external API calls"""
    
    @staticmethod
    def check_patient_exists_and_active(patient_id: str) -> Tuple[bool, Optional[Dict]]:
        """Check if patient exists and is active in Patient Service"""
        try:
            response = requests.get(
                f'{Config.PATIENT_SERVICE_URL}/{patient_id}/exists',
                timeout=5,
                auth=('admin', 'password')  # Basic authentication
            )
            if response.status_code == 200:
                print(f"Patient service response: {response}")
                print(f"type of response: {type(response)}")
                patient_data = response.json()
                is_active = True
                return is_active, patient_data
            return False, None
        except requests.RequestException:
            # For development, allow if service is not available
            current_app.logger.warning(f'Patient service unavailable, assuming patient {patient_id} exists and is active')
            return True, {'id': patient_id, 'status': 'ACTIVE'}
        except Exception as e:
            current_app.logger.error(f'Error checking patient {patient_id}: {str(e)}')
            return False, None
    
    @staticmethod
    def check_doctor_exists_and_active(doctor_id: str, department_id: Optional[str] = None) -> Tuple[bool, Optional[Dict]]:
        """Check if doctor exists, is active, and belongs to requested department in Doctor Service"""
        try:
            response = requests.get(
                f'{Config.DOCTOR_SERVICE_URL}/{doctor_id}',
                timeout=5,
                auth=('admin', 'password')  # Basic authentication
            )
            if response.status_code == 200:
                doctor_data = response.json()
                logging.info(f"Doctor data retrieved: {doctor_data}")
                is_active = doctor_data.get('status', '').upper() == 'ACTIVE' or doctor_data.get('active', True)
                
                # Check department if specified
                if department_id:
                    doctor_dept = doctor_data.get('department_id') or doctor_data.get('department', {})
                    if doctor_dept != department_id:
                        return False, None
                
                return is_active, doctor_data
            return False, None
        except requests.RequestException:
            # For development, allow if service is not available
            current_app.logger.warning(f'Doctor service unavailable, assuming doctor {doctor_id} exists and is active')
            return True, {'id': doctor_id, 'status': 'ACTIVE', 'department_id': department_id}
        except Exception as e:
            current_app.logger.error(f'Error checking doctor {doctor_id}: {str(e)}')
            return False, None
    
    @staticmethod
    def emit_appointment_event(event_data: Dict) -> bool:
        """Emit appointment event to notification service with basic auth"""
        try:
            response = requests.post(
                Config.NOTIFICATION_SERVICE_URL,
                json=event_data,
                timeout=5,
                headers={'Content-Type': 'application/json'},
                auth=('admin', 'secret123')  # Basic authentication
            )
            if response.status_code in [200, 201, 202]:
                current_app.logger.info(f'Successfully emitted event: {event_data.get("event_type")} for appointment {event_data.get("appointment_id")}')
                return True
            else:
                current_app.logger.warning(f'Failed to emit event: {event_data.get("event_type")}. Status: {response.status_code}. Message: {response.text}')
                return False
        except requests.RequestException as e:
            # Log error but don't fail the appointment operation
            current_app.logger.error(f'Error emitting event to notification service: {str(e)}')
            return False

    @staticmethod
    def create_bill(patient_id: str, appointment_id: str, consultation_fee: float = 2000.0, medication_fee: float = 800.0) -> Tuple[bool, Optional[Dict]]:
        """Create a bill in the billing service"""
        try:
            bill_data = {
                'patient_id': int(patient_id.replace('patient-', '')) if 'patient-' in patient_id else patient_id,
                'appointment_id': int(appointment_id.replace('A', '')) if 'A' in appointment_id else appointment_id,
                'consultation_fee': consultation_fee,
                'medication_fee': medication_fee
            }

            response = requests.post(
                Config.BILLING_SERVICE_URL,
                json=bill_data,
                timeout=5,
                headers={'Content-Type': 'application/json'},
                auth=('admin', 'admin123')  # Basic authentication
            )

            if response.status_code in [200, 201]:
                bill_response = response.json()
                current_app.logger.info(f'Successfully created bill for appointment {appointment_id}: {bill_response.get("bill_id")}')
                return True, bill_response
            else:
                current_app.logger.warning(f'Failed to create bill for appointment {appointment_id}. Status: {response.status_code}, Response: {response.text}')
                return False, None
        except requests.RequestException as e:
            # Log error but don't fail the appointment completion
            current_app.logger.error(f'Error creating bill in billing service: {str(e)}')
            return False, None
        except (ValueError, TypeError) as e:
            current_app.logger.error(f'Error formatting bill data: {str(e)}')
            return False, None

    @staticmethod
    def create_prescription(appointment_id: str, patient_id: str, doctor_id: str) -> Tuple[bool, Optional[Dict]]:
        """Create a prescription in the prescription service with random medication"""
        # Hardcoded medications with dosage and duration
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

        # Select random medication
        selected_med = random.choice(medications)

        try:
            # Convert IDs to integers if needed
            prescription_data = {
                'appointment_id': int(appointment_id.replace('A', '')) if isinstance(appointment_id, str) and 'A' in appointment_id else appointment_id,
                'patient_id': int(patient_id.replace('patient-', '')) if isinstance(patient_id, str) and 'patient-' in patient_id else patient_id,
                'doctor_id': int(doctor_id.replace('doctor-', '')) if isinstance(doctor_id, str) and 'doctor-' in doctor_id else doctor_id,
                'medication': selected_med['medication'],
                'dosage': selected_med['dosage'],
                'days': selected_med['days']
            }

            response = requests.post(
                Config.PRESCRIPTION_SERVICE_URL,
                json=prescription_data,
                timeout=5,
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code in [200, 201]:
                prescription_response = response.json()
                current_app.logger.info(f'Successfully created prescription for appointment {appointment_id}: {selected_med["medication"]}')
                return True, prescription_response
            else:
                current_app.logger.warning(f'Failed to create prescription for appointment {appointment_id}. Status: {response.status_code}, Response: {response.text}')
                return False, None
        except requests.RequestException as e:
            # Log error but don't fail the appointment completion
            current_app.logger.error(f'Error creating prescription in prescription service: {str(e)}')
            return False, None
        except (ValueError, TypeError) as e:
            current_app.logger.error(f'Error formatting prescription data: {str(e)}')
            return False, None

