"""CORS extension module.

Provides Flask-CORS instance for Cross-Origin Resource Sharing.
"""

from flask_cors import CORS

# CORS instance
cors = CORS()

def init_cors(app):
    """Initialize CORS extension with Flask application.
    
    Args:
        app: Flask application instance
    """
    cors.init_app(app)
