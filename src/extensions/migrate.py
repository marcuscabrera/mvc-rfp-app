"""Migration extension module.

Provides Flask-Migrate instance for database migrations.
"""

from flask_migrate import Migrate

# Migration instance
migrate = Migrate()

def init_migrate(app, db):
    """Initialize migration extension with Flask application and database.
    
    Args:
        app: Flask application instance
        db: SQLAlchemy database instance
    """
    migrate.init_app(app, db)
