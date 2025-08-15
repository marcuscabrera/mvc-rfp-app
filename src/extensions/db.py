"""Database extension module.

Provides SQLAlchemy database instance for the application.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Database instance
db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    """Initialize database with Flask application.
    
    Args:
        app: Flask application instance
    """
    db.init_app(app)
    migrate.init_app(app, db)
