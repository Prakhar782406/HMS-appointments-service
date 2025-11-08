"""
Health check controller
"""
from flask import Blueprint, jsonify
from models.db import db
from models.appointment import Appointment
from datetime import datetime
import sys

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Comprehensive health check endpoint"""
    health_status = {
        'status': 'healthy',
        'service': 'appointment-service',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'checks': {}
    }
    
    overall_healthy = True
    
    # Database connectivity check
    try:
        db.session.execute(db.text('SELECT 1'))
        health_status['checks']['database'] = {
            'status': 'healthy',
            'message': 'Database connection successful'
        }
    except Exception as e:
        overall_healthy = False
        health_status['checks']['database'] = {
            'status': 'unhealthy',
            'message': f'Database connection failed: {str(e)}'
        }
    
    # Database table check
    try:
        Appointment.query.limit(1).all()
        health_status['checks']['database_tables'] = {
            'status': 'healthy',
            'message': 'Database tables accessible'
        }
    except Exception as e:
        overall_healthy = False
        health_status['checks']['database_tables'] = {
            'status': 'unhealthy',
            'message': f'Database tables not accessible: {str(e)}'
        }
    
    # Python version check
    health_status['checks']['python_version'] = {
        'status': 'healthy',
        'message': sys.version.split()[0]
    }
    
    # Memory check (basic)
    try:
        import psutil
        memory = psutil.virtual_memory()
        health_status['checks']['memory'] = {
            'status': 'healthy',
            'message': f'Available: {memory.percent}% used'
        }
    except ImportError:
        health_status['checks']['memory'] = {
            'status': 'unknown',
            'message': 'psutil not installed'
        }
    
    if not overall_healthy:
        health_status['status'] = 'unhealthy'
        return jsonify(health_status), 503
    
    return jsonify(health_status), 200

@health_bp.route('/ready', methods=['GET'])
def readiness_check():
    """Readiness check - checks if service is ready to accept traffic"""
    try:
        # Check database connection
        db.session.execute(db.text('SELECT 1'))
        # Check if tables exist
        Appointment.query.limit(1).all()
        
        return jsonify({
            'status': 'ready',
            'service': 'appointment-service',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'not ready',
            'service': 'appointment-service',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503

@health_bp.route('/live', methods=['GET'])
def liveness_check():
    """Liveness check - checks if service is alive"""
    return jsonify({
        'status': 'alive',
        'service': 'appointment-service',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

