"""
Data import/export API routes.
"""
from flask import Blueprint, request, jsonify, Response, current_app
import os
from ..database import get_db
from ..services.csv_handler import export_all_data, preview_import, import_csv
from datetime import datetime

data_bp = Blueprint("data", __name__)


@data_bp.route("/export", methods=["GET"])
def export_data():
    """Export all data as a zip of CSV files, saved in DATABASE_DIR."""
    db = get_db()
    zip_bytes = export_all_data(db)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"habit_data_{timestamp}.zip"
    
    export_dir = current_app.config["DATABASE_DIR"]
    os.makedirs(export_dir, exist_ok=True)
    export_path = os.path.join(export_dir, filename)
    
    with open(export_path, "wb") as f:
        f.write(zip_bytes)

    return jsonify({
        "message": "Data exported to database folder",
        "filename": filename,
        "path": export_path
    })


@data_bp.route("/import/preview", methods=["POST"])
def preview_import_data():
    """Preview a CSV file before importing."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if not file.filename.endswith(".csv"):
        return jsonify({"error": "Only CSV files are supported"}), 400

    result = preview_import(file)
    return jsonify(result)


@data_bp.route("/import", methods=["POST"])
def import_data():
    """Import CSV data. Requires table_name parameter."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    table_name = request.form.get("table_name")

    if not table_name or table_name not in ("habits", "entries", "goals", "settings"):
        return jsonify({"error": "Valid table_name required"}), 400

    content = file.read().decode("utf-8-sig")
    db = get_db()
    result = import_csv(db, content, table_name)

    return jsonify(result)
