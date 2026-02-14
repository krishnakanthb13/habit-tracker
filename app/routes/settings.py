"""
Settings API routes.
"""
from flask import Blueprint, request, jsonify
from ..database import get_db

settings_bp = Blueprint("settings", __name__)

VALID_KEYS = {
    "theme", "day_extension", "day_extension_hour",
    "skip_enabled", "animations_enabled",
}


@settings_bp.route("/settings", methods=["GET"])
def get_settings():
    """Get all settings as key-value pairs."""
    db = get_db()
    rows = db.execute("SELECT key, value FROM settings").fetchall()
    settings = {row["key"]: row["value"] for row in rows}
    return jsonify(settings)


@settings_bp.route("/settings", methods=["PUT"])
def update_settings():
    """Update one or more settings."""
    db = get_db()
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    updated = {}
    for key, value in data.items():
        if key not in VALID_KEYS:
            continue
        db.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, str(value)),
        )
        updated[key] = str(value)

    db.commit()
    return jsonify(updated)
