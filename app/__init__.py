"""
Habit Tracker — Flask Application Factory
"""
import os
from flask import Flask
from .config import Config
from .database import init_db, get_db


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure instance/database directories exist
    os.makedirs(app.config["DATABASE_DIR"], exist_ok=True)

    # Initialize database
    with app.app_context():
        init_db(app)

    # Register blueprints
    from .routes.habits import habits_bp
    from .routes.entries import entries_bp
    from .routes.calendar import calendar_bp
    from .routes.settings import settings_bp
    from .routes.data import data_bp
    from .routes.health import health_bp
    from .routes.goals_routes import goals_bp
    from .routes.pages import pages_bp

    app.register_blueprint(habits_bp, url_prefix="/api")
    app.register_blueprint(entries_bp, url_prefix="/api")
    app.register_blueprint(calendar_bp, url_prefix="/api")
    app.register_blueprint(settings_bp, url_prefix="/api")
    app.register_blueprint(data_bp, url_prefix="/api")
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(goals_bp, url_prefix="/api")
    app.register_blueprint(pages_bp)

    # Teardown: close DB connection
    @app.teardown_appcontext
    def close_connection(exception):
        db = getattr(app, "_database", None)
        if db is not None:
            db.close()

    return app
