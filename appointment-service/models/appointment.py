"""
Appointment model
"""
from .db import db
from datetime import datetime, timedelta
import uuid

class Appointment(db.Model):
    """Appointment model"""
    __tablename__ = 'appointments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = db.Column(db.String(36), nullable=False, index=True)
    doctor_id = db.Column(db.String(36), nullable=False, index=True)
    department_id = db.Column(db.String(36), nullable=True)  # For department validation
    
    appointment_date = db.Column(db.DateTime, nullable=False, index=True)
    duration_minutes = db.Column(db.Integer, nullable=False, default=30)
    status = db.Column(db.String(20), nullable=False, default='SCHEDULED')  # SCHEDULED, CONFIRMED, COMPLETED, CANCELLED, NO_SHOW
    
    # Reschedule tracking
    reschedule_count = db.Column(db.Integer, nullable=False, default=0)
    version = db.Column(db.Integer, nullable=False, default=1)  # For optimistic locking
    
    # Additional fields
    reason = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    cancelled_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        """Convert appointment to dictionary"""
        from datetime import timezone
        
        # Convert naive UTC datetimes to ISO format with 'Z' suffix for clarity
        def format_datetime(dt):
            if dt is None:
                return None
            # Add UTC timezone info for ISO format output
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.isoformat().replace('+00:00', 'Z')
        
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'department_id': self.department_id,
            'appointment_date': format_datetime(self.appointment_date),
            'duration_minutes': self.duration_minutes,
            'status': self.status,
            'reschedule_count': self.reschedule_count,
            'version': self.version,
            'reason': self.reason,
            'notes': self.notes,
            'created_at': format_datetime(self.created_at),
            'updated_at': format_datetime(self.updated_at),
            'cancelled_at': format_datetime(self.cancelled_at)
        }
    
    def get_end_time(self):
        """Get appointment end time"""
        return self.appointment_date + timedelta(minutes=self.duration_minutes)

