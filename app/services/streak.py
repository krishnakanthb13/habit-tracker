"""
Streak calculation engine.
"""
from datetime import datetime, timedelta


def calculate_streaks(db, habit_id, skip_enabled=True, effective_today=None):
    """
    Calculate current streak, best streak, and total completions for a habit.

    Streak rules:
    - 'done' entries increment the streak.
    - 'miss' entries (or no entry) break the streak.
    - 'skip' entries are transparent when skip_enabled=True
      (they neither break nor extend the streak).
    - When skip_enabled=False, 'skip' entries are treated as 'miss'.

    Args:
        db: database connection
        habit_id: int
        skip_enabled: bool
        effective_today: str 'YYYY-MM-DD' (defaults to today)

    Returns:
        dict with current_streak, best_streak, total_done
    """
    if effective_today is None:
        effective_today = datetime.now().strftime("%Y-%m-%d")

    # Fetch all entries for this habit, ordered by date descending
    rows = db.execute(
        "SELECT entry_date, status FROM entries WHERE habit_id = ? ORDER BY entry_date DESC",
        (habit_id,),
    ).fetchall()

    # Build a lookup dict
    entry_map = {row["entry_date"]: row["status"] for row in rows}

    # Find the earliest entry date to know how far back to scan
    if not entry_map:
        return {"current_streak": 0, "best_streak": 0, "total_done": 0}

    # Get habit creation date as floor
    habit_row = db.execute(
        "SELECT created_at FROM habits WHERE id = ?", (habit_id,)
    ).fetchone()
    if habit_row and habit_row["created_at"]:
        created = habit_row["created_at"][:10]  # 'YYYY-MM-DD'
    else:
        created = min(entry_map.keys())

    current_streak = 0
    best_streak = 0
    total_done = 0
    temp_streak = 0
    streak_locked = False  # Have we locked in the "current" streak?

    # Walk backwards from effective_today
    day = datetime.strptime(effective_today, "%Y-%m-%d")
    floor_date = datetime.strptime(created, "%Y-%m-%d")

    while day >= floor_date:
        date_str = day.strftime("%Y-%m-%d")
        status = entry_map.get(date_str)

        if status == "done":
            temp_streak += 1
            total_done += 1
        elif status == "skip" and skip_enabled:
            # Transparent — skip this day entirely
            day -= timedelta(days=1)
            continue
        else:
            # 'miss', None, or skip when disabled → streak breaks
            if not streak_locked:
                current_streak = temp_streak
                streak_locked = True
            best_streak = max(best_streak, temp_streak)
            temp_streak = 0

        day -= timedelta(days=1)

    # Final edge: streak might still be running
    if not streak_locked:
        current_streak = temp_streak
    best_streak = max(best_streak, temp_streak)

    return {
        "current_streak": current_streak,
        "best_streak": best_streak,
        "total_done": total_done,
    }
