"""
Application configuration.
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Config:
    """Default configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "habit-tracker-dev-key")
    DATABASE_DIR = os.path.join(BASE_DIR, "database")
    DATABASE_PATH = os.path.join(DATABASE_DIR, "habits.db")
    BACKUP_DIR = os.path.join(DATABASE_DIR, "backups")
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
    PORT = int(os.environ.get("PORT", 5000))
