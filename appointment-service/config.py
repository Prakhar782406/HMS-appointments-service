"""
Configuration settings for the Appointment Service
"""
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    # Database configuration - MySQL
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'root')
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = os.getenv('MYSQL_PORT', '33063')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'appointment_db')
    
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True
    }
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_ALGORITHM = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', '1440'))  # 24 hours
    JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRE_DAYS', '30'))  # 30 days
    
    # External service URLs
    DOCTOR_SERVICE_URL = os.getenv('DOCTOR_SERVICE_URL', 'http://host.docker.internal:8082/v1/doctors')
    PATIENT_SERVICE_URL = os.getenv('PATIENT_SERVICE_URL', 'http://host.docker.internal:8081/v1/patients')
    NOTIFICATION_SERVICE_URL = os.getenv('NOTIFICATION_SERVICE_URL', 'http://host.docker.internal:8000/v1/webhook/events')
    BILLING_SERVICE_URL = os.getenv('BILLING_SERVICE_URL', 'http://host.docker.internal:3002/v1/bills')
    PRESCRIPTION_SERVICE_URL = os.getenv('PRESCRIPTION_SERVICE_URL', 'http://host.docker.internal:3001/api/v1/prescriptions')

    # Business Rules Configuration
    CLINIC_OPEN_HOUR = 9  # 9 AM
    CLINIC_CLOSE_HOUR = 17  # 5 PM
    MIN_LEAD_TIME_HOURS = 2  # Minimum 2 hours lead time
    MAX_RESCHEDULES = 2  # Maximum 2 reschedules per appointment
    RESCHEDULE_CUTOFF_HOURS = 1  # Cannot reschedule within 1 hour of appointment
    
    # API Settings
    API_VERSION = 'v1'


