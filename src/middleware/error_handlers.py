"""Error handlers middleware.

Provides centralized error handling for the application.
"""

from flask import jsonify, request
import logging

def handle_404(error):
    """Handle 404 Not Found errors.
    
    Args:
        error: The error object
        
    Returns:
        JSON response with error details
    """
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource was not found',
        'status_code': 404
    }), 404

def handle_500(error):
    """Handle 500 Internal Server Error.
    
    Args:
        error: The error object
        
    Returns:
        JSON response with error details
    """
    logging.error(f'Internal Server Error: {error}')
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An internal error occurred',
        'status_code': 500
    }), 500

def handle_400(error):
    """Handle 400 Bad Request errors.
    
    Args:
        error: The error object
        
    Returns:
        JSON response with error details
    """
    return jsonify({
        'error': 'Bad Request',
        'message': 'Invalid request data',
        'status_code': 400
    }), 400

def register_error_handlers(app):
    """Register error handlers with Flask app.
    
    Args:
        app: Flask application instance
    """
    app.errorhandler(404)(handle_404)
    app.errorhandler(500)(handle_500)
    app.errorhandler(400)(handle_400)
