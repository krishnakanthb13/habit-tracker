"""
Calendar data API — provides month-view data for all habits.
"""
from flask import Blueprint, request, jsonify
from ..database import get_db
from ..services.day_boundary import get_effective_today
import calendar as cal
from datetime import datetime

calendar_bp = Blueprint("calendar", __name__)


@calendar_bp.route("/calendar", methods=["GET"])
def get_calendar_data():
    """
    Get all habits and their entries for a given month.

    Query params:
        month: 'YYYY-MM' (defaults to current month)

    Returns:
        { month, year, days_in_month, today, habits: [...] }
    """
    db = get_db()
    settings_rows = db.execute("SELECT key, value FROM settings").fetchall()
    settings = {row["key"]: row["value"] for row in settings_rows}
    effective_today = get_effective_today(settings)

    # Parse month param
    month_str = request.args.get("month")
    if month_str:
        try:
            year, month = map(int, month_str.split("-"))
        except (ValueError, AttributeError):
            return jsonify({"error": "Invalid month format. Use YYYY-MM"}), 400
    else:
        today = datetime.strptime(effective_today, "%Y-%m-%d")
        year, month = today.year, today.month

    days_in_month = cal.monthrange(year, month)[1]
    month_start = f"{year:04d}-{month:02d}-01"
    month_end = f"{year:04d}-{month:02d}-{days_in_month:02d}"

    # Get all active habits
    habits = db.execute(
        "SELECT * FROM habits WHERE archived = 0 ORDER BY position ASC, id ASC"
    ).fetchall()

    result_habits = []
    for habit in habits:
        # Get entries for this habit in this month
        entries = db.execute(
            "SELECT entry_date, status, note, id FROM entries "
            "WHERE habit_id = ? AND entry_date BETWEEN ? AND ? "
            "ORDER BY entry_date ASC",
            (habit["id"], month_start, month_end),
        ).fetchall()

        entries_map = {}
        for e in entries:
            entries_map[e["entry_date"]] = {
                "id": e["id"],
                "status": e["status"],
                "note": e["note"],
            }

        result_habits.append({
            "id": habit["id"],
            "name": habit["name"],
            "color": habit["color"],
            "entries": entries_map,
        })

    # First weekday of the month (0=Monday in Python)
    first_weekday = cal.monthrange(year, month)[0]

    return jsonify({
        "year": year,
        "month": month,
        "month_name": cal.month_name[month],
        "days_in_month": days_in_month,
        "first_weekday": first_weekday,
        "today": effective_today,
        "habits": result_habits,
        "skip_enabled": settings.get("skip_enabled", "true") == "true",
    })
