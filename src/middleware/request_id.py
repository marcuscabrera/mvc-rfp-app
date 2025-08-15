"""Request ID middleware.

Provides unique request ID tracking for each HTTP request.
"""

import uuid
from flask import request, g

def generate_request_id():
    """Generate a unique request ID.
    
    Returns:
        str: A unique UUID string
    """
    return str(uuid.uuid4())

def add_request_id():
    """Add request ID to Flask's g object for current request."""
    g.request_id = generate_request_id()

def get_request_id():
    """Get the current request ID.
    
    Returns:
        str: The current request ID or None if not set
    """
    return getattr(g, 'request_id', None)

def register_request_id_middleware(app):
    """Register request ID middleware with Flask app.
    
    Args:
        app: Flask application instance
    """
    @app.before_request
    def before_request():
        """Add request ID before each request."""
        add_request_id()
    
    @app.after_request
    def after_request(response):
        """Add request ID to response headers."""
        request_id = get_request_id()
        if request_id:
            response.headers['X-Request-ID'] = request_id
        return response
