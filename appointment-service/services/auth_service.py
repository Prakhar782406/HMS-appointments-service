"""
Authentication service
"""
from models.user import User
from models.db import db
from config import Config
import jwt
from datetime import datetime, timedelta

class AuthService:
    """Service for authentication operations"""
    
    @staticmethod
    def create_user(username: str, email: str, password: str, role: str = 'user') -> User:
        """Create a new user"""
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            raise ValueError('Username already exists')
        if User.query.filter_by(email=email).first():
            raise ValueError('Email already exists')
        
        user = User(username=username, email=email, password=password, role=role)
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> User:
        """Authenticate user with username and password"""
        user = User.query.filter_by(username=username).first()
        if not user:
            raise ValueError('Invalid credentials')
        
        if not user.is_active:
            raise ValueError('User account is disabled')
        
        if not user.verify_password(password):
            raise ValueError('Invalid credentials')
        
        user.update_last_login()
        return user
    
    @staticmethod
    def generate_token(user: User, token_type: str = 'access') -> str:
        """Generate JWT token for user"""
        if token_type == 'access':
            expire_minutes = Config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            exp = datetime.utcnow() + timedelta(minutes=expire_minutes)
        else:  # refresh
            expire_days = Config.JWT_REFRESH_TOKEN_EXPIRE_DAYS
            exp = datetime.utcnow() + timedelta(days=expire_days)
        
        payload = {
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'exp': exp,
            'iat': datetime.utcnow(),
            'type': token_type
        }
        
        token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM)
        return token
    
    @staticmethod
    def get_user_by_id(user_id: str) -> User:
        """Get user by ID"""
        return User.query.get(user_id)

