"""
Appointment controller
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
from services.appointment_service import AppointmentService
from models.appointment import Appointment
from models.db import db
from middleware.auth import token_required

appointment_bp = Blueprint('appointments', __name__)

@appointment_bp.route('', methods=['POST'])
@token_required
def book_appointment(current_user_id, current_user_role):
    """Book a new appointment"""
    try:
        data = request.json
        patient_id = data.get('patient_id')
        doctor_id = data.get('doctor_id')
        department_id = data.get('department_id')
        appointment_date_str = data.get('appointment_date')
        duration_minutes = data.get('duration_minutes', 30)
        reason = data.get('reason')
        notes = data.get('notes')
        
        if not all([patient_id, doctor_id, appointment_date_str]):
            return jsonify({'error': 'patient_id, doctor_id, and appointment_date are required'}), 400
        
        # Parse datetime and convert to UTC naive (for database compatibility)
        try:
            # Handle both 'Z' and timezone offset formats
            if appointment_date_str.endswith('Z'):
                appointment_date = datetime.fromisoformat(appointment_date_str.replace('Z', '+00:00'))
            else:
                appointment_date = datetime.fromisoformat(appointment_date_str)
            
            # Convert timezone-aware datetime to UTC naive datetime
            if appointment_date.tzinfo is not None:
                appointment_date = appointment_date.astimezone(timezone.utc).replace(tzinfo=None)
        except ValueError as e:
            return jsonify({'error': f'Invalid appointment_date format: {str(e)}'}), 400
        
        appointment = AppointmentService.book_appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            department_id=department_id,
            duration_minutes=duration_minutes,
            reason=reason,
            notes=notes
        )
        
        return jsonify({
            'message': 'Appointment booked successfully',
            'appointment': appointment.to_dict()
        }), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@appointment_bp.route('/<appointment_id>', methods=['GET'])
@token_required
def get_appointment(current_user_id, current_user_role, appointment_id):
    """Get appointment by ID"""
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404
    
    return jsonify(appointment.to_dict()), 200

@appointment_bp.route('/<appointment_id>/reschedule', methods=['POST'])
@token_required
def reschedule_appointment(current_user_id, current_user_role, appointment_id):
    """Reschedule an existing appointment"""
    try:
        data = request.json
        new_appointment_date_str = data.get('appointment_date')
        new_duration_minutes = data.get('duration_minutes')
        reason = data.get('reason')
        notes = data.get('notes')
        
        if not new_appointment_date_str:
            return jsonify({'error': 'appointment_date is required for rescheduling'}), 400
        
        # Parse datetime and convert to UTC naive (for database compatibility)
        try:
            # Handle both 'Z' and timezone offset formats
            if new_appointment_date_str.endswith('Z'):
                new_appointment_date = datetime.fromisoformat(new_appointment_date_str.replace('Z', '+00:00'))
            else:
                new_appointment_date = datetime.fromisoformat(new_appointment_date_str)
            
            # Convert timezone-aware datetime to UTC naive datetime
            if new_appointment_date.tzinfo is not None:
                new_appointment_date = new_appointment_date.astimezone(timezone.utc).replace(tzinfo=None)
        except ValueError as e:
            return jsonify({'error': f'Invalid appointment_date format: {str(e)}'}), 400
        
        appointment = AppointmentService.reschedule_appointment(
            appointment_id=appointment_id,
            new_appointment_date=new_appointment_date,
            new_duration_minutes=new_duration_minutes,
            reason=reason,
            notes=notes
        )
        
        return jsonify({
            'message': 'Appointment rescheduled successfully',
            'appointment': appointment.to_dict()
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@appointment_bp.route('/<appointment_id>/cancel', methods=['POST'])
@token_required
def cancel_appointment(current_user_id, current_user_role, appointment_id):
    """Cancel an appointment"""
    try:
        data = request.json or {}
        cancellation_reason = data.get('reason')
        
        appointment = AppointmentService.cancel_appointment(
            appointment_id=appointment_id,
            cancellation_reason=cancellation_reason
        )
        
        return jsonify({
            'message': 'Appointment cancelled successfully.',
            'appointment': appointment.to_dict()
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@appointment_bp.route('/<appointment_id>/confirm', methods=['POST'])
@token_required
def confirm_appointment(current_user_id, current_user_role, appointment_id):
    """Confirm an appointment"""
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404
    
    if appointment.status != 'SCHEDULED':
        return jsonify({'error': f'Appointment is already {appointment.status.lower()}'}), 400
    
    appointment.status = 'CONFIRMED'
    appointment.version += 1
    appointment.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Appointment confirmed',
        'appointment': appointment.to_dict()
    }), 200

@appointment_bp.route('/<appointment_id>/complete', methods=['POST'])
@token_required
def complete_appointment(current_user_id, current_user_role, appointment_id):
    """Mark an appointment as completed"""
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404
    
    if appointment.status not in ['CONFIRMED', 'SCHEDULED']:
        return jsonify({'error': f'Cannot complete appointment with status {appointment.status}'}), 400
    
    appointment.status = 'COMPLETED'
    appointment.version += 1
    appointment.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Appointment marked as completed',
        'appointment': appointment.to_dict()
    }), 200

@appointment_bp.route('/patient/<patient_id>', methods=['GET'])
@token_required
def get_appointments_by_patient(current_user_id, current_user_role, patient_id):
    """Get all appointments for a patient"""
    status = request.args.get('status')
    query = Appointment.query.filter_by(patient_id=patient_id)
    
    if status:
        query = query.filter_by(status=status)
    
    appointments = query.order_by(Appointment.appointment_date.desc()).all()
    return jsonify([appointment.to_dict() for appointment in appointments]), 200

@appointment_bp.route('/doctor/<doctor_id>', methods=['GET'])
@token_required
def get_appointments_by_doctor(current_user_id, current_user_role, doctor_id):
    """Get all appointments for a doctor"""
    status = request.args.get('status')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Appointment.query.filter_by(doctor_id=doctor_id)
    
    if status:
        query = query.filter_by(status=status)
    
    if start_date:
        try:
            # Handle both 'Z' and timezone offset formats
            if start_date.endswith('Z'):
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            else:
                start_dt = datetime.fromisoformat(start_date)
            # Convert to UTC naive if timezone-aware
            if start_dt.tzinfo is not None:
                start_dt = start_dt.astimezone(timezone.utc).replace(tzinfo=None)
            query = query.filter(Appointment.appointment_date >= start_dt)
        except ValueError:
            return jsonify({'error': 'Invalid start_date format'}), 400
    
    if end_date:
        try:
            # Handle both 'Z' and timezone offset formats
            if end_date.endswith('Z'):
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            else:
                end_dt = datetime.fromisoformat(end_date)
            # Convert to UTC naive if timezone-aware
            if end_dt.tzinfo is not None:
                end_dt = end_dt.astimezone(timezone.utc).replace(tzinfo=None)
            query = query.filter(Appointment.appointment_date <= end_dt)
        except ValueError:
            return jsonify({'error': 'Invalid end_date format'}), 400
    
    appointments = query.order_by(Appointment.appointment_date.asc()).all()
    return jsonify([appointment.to_dict() for appointment in appointments]), 200

