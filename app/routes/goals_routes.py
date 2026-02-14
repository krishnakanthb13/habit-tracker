"""
Goals API routes.
"""
from flask import Blueprint, request, jsonify
from ..database import get_db
from ..services.goals import evaluate_goal
from ..services.day_boundary import get_effective_today

goals_bp = Blueprint("goals", __name__)


@goals_bp.route("/habits/<int:habit_id>/goals", methods=["GET"])
def get_goal(habit_id):
    """Get goal and progress for a habit."""
    db = get_db()
    settings_rows = db.execute("SELECT key, value FROM settings").fetchall()
    settings = {row["key"]: row["value"] for row in settings_rows}
    effective_today = get_effective_today(settings)

    goal = evaluate_goal(db, habit_id, effective_today)
    if goal is None:
        return jsonify({"message": "No goal set"}), 200

    return jsonify(goal)


@goals_bp.route("/habits/<int:habit_id>/goals", methods=["POST"])
def set_goal(habit_id):
    """Set or update goal for a habit."""
    db = get_db()
    data = request.get_json()

    goal_type = data.get("goal_type", "daily")
    if goal_type not in ("daily", "weekly", "custom"):
        return jsonify({"error": "Invalid goal_type"}), 400

    target = data.get("target", 1)
    period_days = data.get("period_days", 7)

    db.execute(
        "INSERT OR REPLACE INTO goals (habit_id, goal_type, target, period_days) "
        "VALUES (?, ?, ?, ?)",
        (habit_id, goal_type, target, period_days),
    )
    db.commit()

    return jsonify({
        "habit_id": habit_id,
        "goal_type": goal_type,
        "target": target,
        "period_days": period_days,
    }), 201


@goals_bp.route("/habits/<int:habit_id>/goals", methods=["DELETE"])
def delete_goal(habit_id):
    """Remove goal for a habit."""
    db = get_db()
    db.execute("DELETE FROM goals WHERE habit_id = ?", (habit_id,))
    db.commit()
    return jsonify({"message": "Goal removed", "habit_id": habit_id})
