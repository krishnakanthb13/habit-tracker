"""
Habit CRUD API routes.
"""
from flask import Blueprint, request, jsonify
from ..database import get_db
from ..services.streak import calculate_streaks
from ..services.goals import evaluate_goal
from ..services.day_boundary import get_effective_today

habits_bp = Blueprint("habits", __name__)


def _get_settings_dict(db):
    """Helper to load settings as a dict."""
    rows = db.execute("SELECT key, value FROM settings").fetchall()
    return {row["key"]: row["value"] for row in rows}


@habits_bp.route("/habits", methods=["GET"])
def list_habits():
    """List all active habits with streak data."""
    db = get_db()
    settings = _get_settings_dict(db)
    skip_enabled = settings.get("skip_enabled", "true") == "true"
    effective_today = get_effective_today(settings)

    habits = db.execute(
        "SELECT * FROM habits WHERE archived = 0 ORDER BY position ASC, id ASC"
    ).fetchall()

    # NOTE: Technical Debt - N+1 Query Pattern
    # This loop executes multiple queries (streak, goal, today_status) for each habit.
    # While inefficient for large-scale SaaS, it is a conscious design choice for this
    # local app to keep service logic simple and modular. For hundreds of habits, 
    # these should be refactored into a single bulk-fetch query.
    result = []
    for habit in habits:
        streaks = calculate_streaks(db, habit["id"], skip_enabled, effective_today)
        goal = evaluate_goal(db, habit["id"], effective_today)

        # Get today's entry status
        today_entry = db.execute(
            "SELECT status, note FROM entries WHERE habit_id = ? AND entry_date = ?",
            (habit["id"], effective_today),
        ).fetchone()

        result.append({
            "id": habit["id"],
            "name": habit["name"],
            "description": habit["description"],
            "color": habit["color"],
            "position": habit["position"],
            "created_at": habit["created_at"],
            "current_streak": streaks["current_streak"],
            "best_streak": streaks["best_streak"],
            "total_done": streaks["total_done"],
            "today_status": today_entry["status"] if today_entry else None,
            "today_note": today_entry["note"] if today_entry else "",
            "goal": goal,
        })

    return jsonify(result)


@habits_bp.route("/habits", methods=["POST"])
def create_habit():
    """Create a new habit."""
    db = get_db()
    data = request.get_json()

    # Trimming and Sanitization
    name = data.get("name", "").strip()
    description = data.get("description", "").strip()
    color = data.get("color", "#4CAF50").strip()

    if not name:
        return jsonify({"error": "Name is required"}), 400

    # Limit lengths to prevent overflow/abuse
    name = name[:100]
    description = description[:500]
    color = color[:20]

    # Get max position
    row = db.execute("SELECT MAX(position) as max_pos FROM habits").fetchone()
    next_pos = (row["max_pos"] or 0) + 1

    cursor = db.execute(
        "INSERT INTO habits (name, description, color, position) VALUES (?, ?, ?, ?)",
        (name, description, color, next_pos),
    )
    db.commit()

    habit = db.execute("SELECT * FROM habits WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return jsonify({
        "id": habit["id"],
        "name": habit["name"],
        "description": habit["description"],
        "color": habit["color"],
        "position": habit["position"],
        "created_at": habit["created_at"],
    }), 201


@habits_bp.route("/habits/<int:habit_id>", methods=["PUT"])
def update_habit(habit_id):
    """Update a habit."""
    db = get_db()
    data = request.get_json()

    habit = db.execute("SELECT * FROM habits WHERE id = ?", (habit_id,)).fetchone()
    if not habit:
        return jsonify({"error": "Habit not found"}), 404

    # Trimming and Sanitization
    name = data.get("name", habit["name"]).strip()[:100]
    description = data.get("description", habit["description"]).strip()[:500]
    color = data.get("color", habit["color"]).strip()[:20]
    position = data.get("position", habit["position"])

    db.execute(
        "UPDATE habits SET name = ?, description = ?, color = ?, position = ? WHERE id = ?",
        (name, description, color, position, habit_id),
    )
    db.commit()

    updated = db.execute("SELECT * FROM habits WHERE id = ?", (habit_id,)).fetchone()
    return jsonify({
        "id": updated["id"],
        "name": updated["name"],
        "description": updated["description"],
        "color": updated["color"],
        "position": updated["position"],
    })


@habits_bp.route("/habits/<int:habit_id>", methods=["DELETE"])
def archive_habit(habit_id):
    """Archive a habit (soft delete)."""
    db = get_db()

    habit = db.execute("SELECT * FROM habits WHERE id = ?", (habit_id,)).fetchone()
    if not habit:
        return jsonify({"error": "Habit not found"}), 404

    db.execute("UPDATE habits SET archived = 1 WHERE id = ?", (habit_id,))
    db.commit()

    return jsonify({"message": "Habit archived", "id": habit_id})


@habits_bp.route("/habits/<int:habit_id>/unarchive", methods=["POST"])
def unarchive_habit(habit_id):
    """Restore an archived habit."""
    db = get_db()
    db.execute("UPDATE habits SET archived = 0 WHERE id = ?", (habit_id,))
    db.commit()
    return jsonify({"message": "Habit restored", "id": habit_id})


@habits_bp.route("/habits/<int:habit_id>/hard-delete", methods=["DELETE"])
def hard_delete_habit(habit_id):
    """Permanently delete a habit and all records."""
    db = get_db()
    db.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
    db.commit()
    return jsonify({"message": "Habit permanently deleted", "id": habit_id})


@habits_bp.route("/habits/archived", methods=["GET"])
def list_archived_habits():
    """List all archived habits."""
    db = get_db()
    habits = db.execute("SELECT * FROM habits WHERE archived = 1").fetchall()
    return jsonify([dict(h) for h in habits])


@habits_bp.route("/habits/reorder", methods=["PUT"])
def reorder_habits():
    """Reorder habits by providing a list of IDs in desired order."""
    db = get_db()
    data = request.get_json()
    order = data.get("order", [])

    for position, habit_id in enumerate(order):
        db.execute(
            "UPDATE habits SET position = ? WHERE id = ?",
            (position, habit_id),
        )
    db.commit()

    return jsonify({"message": "Reordered", "order": order})
