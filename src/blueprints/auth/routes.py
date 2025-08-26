"""Auth Blueprint Routes

This module contains authentication-related routes.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

# Create the auth blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint (mock).

    In a real app, you'd verify username and password here.
    """
    # For this mock, we'll just create a token for a test user.
    # The frontend doesn't even send user/pass, so we don't need to check it.
    access_token = create_access_token(identity="testuser")
    return jsonify(access_token=access_token)

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """User logout endpoint."""
    # In a real app with token blocklisting, you'd handle that here.
    return jsonify({"msg": "Successfully logged out"}), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    """Get current user profile (mock)."""
    current_user = get_jwt_identity()
    # In a real app, you would fetch user details from the database.
    return jsonify(
        user={
            "username": current_user,
            "email": f"{current_user}@example.com",
            "name": "Test User"
        }
    ), 200

@auth_bp.route('/health', methods=['GET'])
def auth_health():
    """Auth service health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'auth',
        'message': 'Authentication service is running'
    })
