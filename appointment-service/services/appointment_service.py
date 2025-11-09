"""
Appointment business logic service
"""
from models.appointment import Appointment
from models.db import db
from services.external_service import ExternalService
from config import Config
from datetime import datetime, timedelta, time
from typing import Optional, Tuple

class AppointmentService:
    """Service for appointment business logic"""
    
    @staticmethod
    def _format_datetime(dt: datetime) -> str:
        """Format datetime to ISO format with Z suffix"""
        from datetime import timezone
        if dt is None:
            return None
        # Add UTC timezone info for ISO format output
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat().replace('+00:00', 'Z')

    @staticmethod
    def validate_clinic_hours(appointment_date: datetime) -> Tuple[bool, Optional[str]]:
        """Validate that appointment is within clinic hours (9 AM - 5 PM UTC)"""
        appointment_time = appointment_date.time()
        clinic_open = time(Config.CLINIC_OPEN_HOUR, 0)
        clinic_close = time(Config.CLINIC_CLOSE_HOUR, 0)
        
        if appointment_time < clinic_open or appointment_time >= clinic_close:
            return False, f'Appointment must be within clinic hours ({Config.CLINIC_OPEN_HOUR}:00 - {Config.CLINIC_CLOSE_HOUR}:00 UTC)'
        
        return True, None
    
    @staticmethod
    def validate_lead_time(appointment_date: datetime) -> Tuple[bool, Optional[str]]:
        """Validate that appointment is at least 2 hours from now"""
        now = datetime.utcnow()
        time_diff = (appointment_date - now).total_seconds() / 3600
        
        if time_diff < Config.MIN_LEAD_TIME_HOURS:
            return False, f'Appointment must be at least {Config.MIN_LEAD_TIME_HOURS} hours from now'
        
        return True, None
    
    @staticmethod
    def check_doctor_availability(doctor_id: str, appointment_date: datetime, duration_minutes: int, exclude_appointment_id: Optional[str] = None) -> bool:
        """Check if doctor is available at the given time (no slot collision)"""
        end_time = appointment_date + timedelta(minutes=duration_minutes)
        
        query = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.status.in_(['SCHEDULED', 'CONFIRMED'])
        )
        
        if exclude_appointment_id:
            query = query.filter(Appointment.id != exclude_appointment_id)
        
        existing_appointments = query.all()
        
        for existing in existing_appointments:
            existing_end = existing.appointment_date + timedelta(minutes=existing.duration_minutes)
            if appointment_date < existing_end and end_time > existing.appointment_date:
                return False
        
        return True
    
    @staticmethod
    def check_patient_availability(patient_id: str, appointment_date: datetime, duration_minutes: int, exclude_appointment_id: Optional[str] = None) -> bool:
        """Check if patient has no overlapping appointments"""
        end_time = appointment_date + timedelta(minutes=duration_minutes)
        
        query = Appointment.query.filter(
            Appointment.patient_id == patient_id,
            Appointment.status.in_(['SCHEDULED', 'CONFIRMED'])
        )
        
        if exclude_appointment_id:
            query = query.filter(Appointment.id != exclude_appointment_id)
        
        existing_appointments = query.all()
        
        for existing in existing_appointments:
            existing_end = existing.appointment_date + timedelta(minutes=existing.duration_minutes)
            if appointment_date < existing_end and end_time > existing.appointment_date:
                return False
        
        return True
    
    @staticmethod
    def book_appointment(patient_id: str, doctor_id: str, appointment_date: datetime, 
                        department_id: Optional[str] = None, duration_minutes: int = 30,
                        reason: Optional[str] = None, notes: Optional[str] = None) -> Appointment:
        """Book a new appointment with all validations"""
        # Validate patient
        is_active, _ = ExternalService.check_patient_exists_and_active(patient_id)
        if not is_active:
            raise ValueError('Patient not found or not active')
        
        # Validate doctor
        is_active, _ = ExternalService.check_doctor_exists_and_active(doctor_id, department_id)
        if not is_active:
            raise ValueError('Doctor not found, not active, or does not belong to the requested department')
        
        # Validate clinic hours
        is_valid, error_msg = AppointmentService.validate_clinic_hours(appointment_date)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Validate lead time
        is_valid, error_msg = AppointmentService.validate_lead_time(appointment_date)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Check doctor availability
        if not AppointmentService.check_doctor_availability(doctor_id, appointment_date, duration_minutes):
            raise ValueError('Doctor is not available at this time slot (slot collision)')
        
        # Check patient availability
        if not AppointmentService.check_patient_availability(patient_id, appointment_date, duration_minutes):
            raise ValueError('Patient already has an appointment at this time slot')
        
        # Create appointment
        appointment = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            department_id=department_id,
            appointment_date=appointment_date,
            duration_minutes=duration_minutes,
            status='SCHEDULED',
            reschedule_count=0,
            version=1,
            reason=reason,
            notes=notes
        )
        
        db.session.add(appointment)
        db.session.commit()

        # Emit appointment.scheduled event
        end_time = appointment_date + timedelta(minutes=duration_minutes)
        event_data = {
            'event_type': 'appointment.scheduled',
            'appointment_id': appointment.id,
            'patient_id': patient_id,
            'doctor_id': doctor_id,
            'department': department_id,
            'slot': {
                'start_time': AppointmentService._format_datetime(appointment_date),
                'end_time': AppointmentService._format_datetime(end_time)
            },
            'status': 'SCHEDULED'
        }
        ExternalService.emit_appointment_event(event_data)

        return appointment
    
    @staticmethod
    def reschedule_appointment(appointment_id: str, new_appointment_date: datetime, 
                              new_duration_minutes: Optional[int] = None, 
                              reason: Optional[str] = None, notes: Optional[str] = None) -> Appointment:
        """Reschedule an appointment with validations"""
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            raise ValueError('Appointment not found')
        
        if appointment.status not in ['SCHEDULED', 'CONFIRMED']:
            raise ValueError(f'Cannot reschedule appointment with status {appointment.status}')
        
        # Check reschedule count
        if appointment.reschedule_count >= Config.MAX_RESCHEDULES:
            raise ValueError(f'Maximum reschedule limit reached ({Config.MAX_RESCHEDULES} reschedules allowed)')
        
        # Check cut-off time
        time_until_appointment = (appointment.appointment_date - datetime.utcnow()).total_seconds() / 3600
        if time_until_appointment < Config.RESCHEDULE_CUTOFF_HOURS:
            raise ValueError(f'Cannot reschedule within {Config.RESCHEDULE_CUTOFF_HOURS} hour(s) of appointment start time')
        
        # Validate clinic hours
        is_valid, error_msg = AppointmentService.validate_clinic_hours(new_appointment_date)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Validate lead time
        is_valid, error_msg = AppointmentService.validate_lead_time(new_appointment_date)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Check availability
        duration = new_duration_minutes or appointment.duration_minutes
        if not AppointmentService.check_doctor_availability(appointment.doctor_id, new_appointment_date, duration, exclude_appointment_id=appointment.id):
            raise ValueError('Doctor is not available at the new time slot')
        
        if not AppointmentService.check_patient_availability(appointment.patient_id, new_appointment_date, duration, exclude_appointment_id=appointment.id):
            raise ValueError('Patient already has an appointment at the new time slot')
        
        # Store old slot details for event
        old_start = appointment.appointment_date
        old_end = old_start + timedelta(minutes=appointment.duration_minutes)

        # Update appointment
        appointment.appointment_date = new_appointment_date
        appointment.duration_minutes = duration
        appointment.reschedule_count += 1
        appointment.version += 1
        appointment.status = 'SCHEDULED'
        appointment.updated_at = datetime.utcnow()
        
        if reason:
            appointment.reason = reason
        if notes:
            appointment.notes = notes
        
        db.session.commit()

        # Emit appointment.rescheduled event
        new_end = new_appointment_date + timedelta(minutes=duration)
        event_data = {
            'event_type': 'appointment.rescheduled',
            'appointment_id': appointment.id,
            'old_slot': {
                'start_time': AppointmentService._format_datetime(old_start),
                'end_time': AppointmentService._format_datetime(old_end)
            },
            'new_slot': {
                'start_time': AppointmentService._format_datetime(new_appointment_date),
                'end_time': AppointmentService._format_datetime(new_end)
            },
            'version': appointment.version,
            'reschedule_count': appointment.reschedule_count,
            'status': 'SCHEDULED'
        }
        ExternalService.emit_appointment_event(event_data)

        return appointment
    
    @staticmethod
    def cancel_appointment(appointment_id: str, cancellation_reason: Optional[str] = None) -> Appointment:
        """Cancel an appointment"""
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            raise ValueError('Appointment not found')
        
        if appointment.status in ['CANCELLED', 'COMPLETED']:
            raise ValueError(f'Appointment is already {appointment.status.lower()}')
        
        appointment.status = 'CANCELLED'
        appointment.cancelled_at = datetime.utcnow()
        appointment.version += 1
        if cancellation_reason:
            appointment.notes = f"{appointment.notes or ''}\nCancellation reason: {cancellation_reason}".strip()
        
        db.session.commit()
        
        # Emit appointment.cancelled event
        event_data = {
            'event_type': 'appointment.cancelled',
            'appointment_id': appointment.id,
            'patient_id': appointment.patient_id,
            'doctor_id': appointment.doctor_id,
            'cancelled_at': AppointmentService._format_datetime(appointment.cancelled_at),
            'policy_applied': '50_percent_fee',  # Default policy - can be enhanced based on business logic
            'refund_amount': 500.0,  # Default refund - can be enhanced based on business logic
            'status': 'CANCELLED'
        }
        ExternalService.emit_appointment_event(event_data)

        return appointment

