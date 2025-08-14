"""Security headers middleware.

Provides middleware for adding security headers to responses.
"""

from flask import request, g

def add_security_headers(response):
    """Add security headers to response.
    
    Args:
        response: Flask response object
        
    Returns:
        Flask response object with security headers
    """
    # Add basic security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    return response

def register_security_middleware(app):
    """Register security headers middleware with Flask app.
    
    Args:
        app: Flask application instance
    """
    @app.after_request
    def security_headers_middleware(response):
        return add_security_headers(response)
