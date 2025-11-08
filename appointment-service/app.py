"""
Appointment Service - Main Application
MVC Architecture with JWT Authentication
"""
from flask import Flask
from config import Config
from models.db import db
from models.user import User
from controllers.auth_controller import auth_bp
from controllers.appointment_controller import appointment_bp
from controllers.health_controller import health_bp

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints (controllers)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(appointment_bp, url_prefix=f'/api/{Config.API_VERSION}/appointments')
    app.register_blueprint(health_bp, url_prefix='')
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create default admin user if it doesn't exist
        if not User.query.filter_by(username='admin').first():
            from services.auth_service import AuthService
            try:
                admin_user = AuthService.create_user(
                    username='admin',
                    email='admin@hospital.com',
                    password='admin123',
                    role='admin'
                )
                app.logger.info('Default admin user created: admin/admin123')
            except Exception as e:
                app.logger.warning(f'Could not create default admin user: {e}')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5001, debug=True)
