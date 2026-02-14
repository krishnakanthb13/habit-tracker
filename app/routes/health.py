"""
Database health check and repair API routes.
"""
from flask import Blueprint, jsonify, current_app
from ..services.db_repair import integrity_check, create_backup, repair_database

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def check_health():
    """Run integrity check on the database."""
    db_path = current_app.config["DATABASE_PATH"]
    result = integrity_check(db_path)
    status_code = 200 if result["ok"] else 500
    return jsonify(result), status_code


@health_bp.route("/health/backup", methods=["POST"])
def backup_db():
    """Create a manual backup of the database."""
    db_path = current_app.config["DATABASE_PATH"]
    backup_dir = current_app.config["BACKUP_DIR"]

    try:
        backup_path = create_backup(db_path, backup_dir)
        return jsonify({"message": "Backup created", "path": backup_path})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@health_bp.route("/health/repair", methods=["POST"])
def repair_db():
    """Attempt to repair the database."""
    db_path = current_app.config["DATABASE_PATH"]
    backup_dir = current_app.config["BACKUP_DIR"]

    result = repair_database(db_path, backup_dir)
    status_code = 200 if result["success"] else 500
    return jsonify(result), status_code
