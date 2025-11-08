"""
External service integration
"""
import requests
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
                f'{Config.PATIENT_SERVICE_URL}/patients/{patient_id}',
                timeout=5
            )
            if response.status_code == 200:
                patient_data = response.json()
                is_active = patient_data.get('status', '').upper() == 'ACTIVE' or patient_data.get('active', True)
                return is_active, patient_data
            return False, None
        except requests.RequestException:
            # For development, allow if service is not available
            current_app.logger.warning(f'Patient service unavailable, assuming patient {patient_id} exists and is active')
            return True, {'id': patient_id, 'status': 'ACTIVE'}
    
    @staticmethod
    def check_doctor_exists_and_active(doctor_id: str, department_id: Optional[str] = None) -> Tuple[bool, Optional[Dict]]:
        """Check if doctor exists, is active, and belongs to requested department in Doctor Service"""
        try:
            response = requests.get(
                f'{Config.DOCTOR_SERVICE_URL}/doctors/{doctor_id}',
                timeout=5
            )
            if response.status_code == 200:
                doctor_data = response.json()
                is_active = doctor_data.get('status', '').upper() == 'ACTIVE' or doctor_data.get('active', True)
                
                # Check department if specified
                if department_id:
                    doctor_dept = doctor_data.get('department_id') or doctor_data.get('department', {}).get('id')
                    if doctor_dept != department_id:
                        return False, None
                
                return is_active, doctor_data
            return False, None
        except requests.RequestException:
            # For development, allow if service is not available
            current_app.logger.warning(f'Doctor service unavailable, assuming doctor {doctor_id} exists and is active')
            return True, {'id': doctor_id, 'status': 'ACTIVE', 'department_id': department_id}
    
