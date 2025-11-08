"""
JWT Authentication middleware
"""
from functools import wraps
from flask import request, jsonify
import jwt
from datetime import datetime
from config import Config

def token_required(f):
    """Decorator to require JWT token authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # Extract token from "Bearer <token>"
                token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
            except IndexError:
                return jsonify({'error': 'Invalid authorization header format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # Decode and verify token
            data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
            current_user_id = data.get('user_id')
            current_user_role = data.get('role')
            current_username = data.get('username')
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Add user info to request context
        request.current_user_id = current_user_id
        request.current_user_role = current_user_role
        request.current_username = current_username
        
        return f(current_user_id, current_user_role, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    @token_required
    def decorated(current_user_id, current_user_role, *args, **kwargs):
        if current_user_role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(current_user_id, current_user_role, *args, **kwargs)
    
    return decorated

def optional_token(f):
    """Decorator for optional authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
            except IndexError:
                pass
        
        if token:
            try:
                data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
                request.current_user_id = data.get('user_id')
                request.current_user_role = data.get('role')
                request.current_username = data.get('username')
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                pass
        
        return f(*args, **kwargs)
    
    return decorated


