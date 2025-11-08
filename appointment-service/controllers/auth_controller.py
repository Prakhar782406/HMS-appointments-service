"""
Authentication controller
"""
from flask import Blueprint, request, jsonify
from services.auth_service import AuthService
from middleware.auth import token_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'user')
        
        if not all([username, email, password]):
            return jsonify({'error': 'username, email, and password are required'}), 400
        
        user = AuthService.create_user(username, email, password, role)
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login and get JWT token"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not all([username, password]):
            return jsonify({'error': 'username and password are required'}), 400
        
        user = AuthService.authenticate_user(username, password)
        access_token = AuthService.generate_token(user, 'access')
        refresh_token = AuthService.generate_token(user, 'refresh')
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': 1440,  # 24 hours in minutes
            'user': user.to_dict()
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/token', methods=['POST'])
def get_token():
    """Get JWT token (alias for login)"""
    return login()

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user_id, current_user_role):
    """Get current user information"""
    try:
        user = AuthService.get_user_by_id(current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


