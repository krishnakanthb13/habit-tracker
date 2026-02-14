"""
Goal evaluation engine.
"""
from datetime import datetime, timedelta


def evaluate_goal(db, habit_id, effective_today=None):
    """
    Evaluate the goal progress for a habit.

    Returns:
        dict with goal_type, target, current, met (bool), or None if no goal set.
    """
    if effective_today is None:
        effective_today = datetime.now().strftime("%Y-%m-%d")

    goal = db.execute(
        "SELECT goal_type, target, period_days FROM goals WHERE habit_id = ?",
        (habit_id,),
    ).fetchone()

    if goal is None:
        return None

    goal_type = goal["goal_type"]
    target = goal["target"]
    period_days = goal["period_days"] or 7
    today = datetime.strptime(effective_today, "%Y-%m-%d")

    if goal_type == "daily":
        row = db.execute(
            "SELECT status FROM entries WHERE habit_id = ? AND entry_date = ?",
            (habit_id, effective_today),
        ).fetchone()
        current = 1 if row and row["status"] == "done" else 0
        return {
            "goal_type": "daily",
            "target": 1,
            "current": current,
            "met": current >= 1,
        }

    elif goal_type == "weekly":
        # Monday-based week
        weekday = today.weekday()  # 0=Monday
        week_start = (today - timedelta(days=weekday)).strftime("%Y-%m-%d")
        week_end = effective_today

        row = db.execute(
            "SELECT COUNT(*) as cnt FROM entries "
            "WHERE habit_id = ? AND status = 'done' "
            "AND entry_date BETWEEN ? AND ?",
            (habit_id, week_start, week_end),
        ).fetchone()
        current = row["cnt"]
        return {
            "goal_type": "weekly",
            "target": target,
            "current": current,
            "met": current >= target,
        }

    elif goal_type == "custom":
        period_start = (today - timedelta(days=period_days - 1)).strftime("%Y-%m-%d")

        row = db.execute(
            "SELECT COUNT(*) as cnt FROM entries "
            "WHERE habit_id = ? AND status = 'done' "
            "AND entry_date BETWEEN ? AND ?",
            (habit_id, period_start, effective_today),
        ).fetchone()
        current = row["cnt"]
        return {
            "goal_type": "custom",
            "target": target,
            "current": current,
            "met": current >= target,
            "period_days": period_days,
        }

    return None
