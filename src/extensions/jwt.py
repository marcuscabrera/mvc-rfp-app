"""JWT extension module.

Provides Flask-JWT-Extended instance for JWT token management.
"""

from flask_jwt_extended import JWTManager

# JWT Manager instance
jwt = JWTManager()

def init_jwt(app):
    """Initialize JWT extension with Flask application.
    
    Args:
        app: Flask application instance
    """
    jwt.init_app(app)
