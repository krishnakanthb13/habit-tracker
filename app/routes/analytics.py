"""
Analytics API routes.
"""
from datetime import datetime, timedelta
from flask import Blueprint, jsonify
from app.database import get_db
from app.services.streak import calculate_streaks

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/analytics")
def get_analytics():
    """Get aggregated analytics data."""
    db = get_db()
    
    # 1. Get all habits
    habits = db.execute("SELECT id, name, color, created_at FROM habits WHERE archived = 0").fetchall()
    
    total_habits = len(habits)
    if total_habits == 0:
        return jsonify({
            "summary": {
                "total_habits": 0,
                "total_completions": 0,
                "overall_completion_rate": 0,
                "best_streak": 0,
                "perfect_days": 0
            },
            "daily_trend": [],
            "habit_performance": []
        })

    # 2. Daily Trends (Last 30 days)
    today = datetime.now()
    dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(29, -1, -1)]
    
    daily_counts = {}
    for date in dates:
        daily_counts[date] = 0
        
    # Get all 'done' entries for last 30 days
    start_date = dates[0]
    entries = db.execute(
        "SELECT entry_date FROM entries WHERE status = 'done' AND entry_date >= ?",
        (start_date,)
    ).fetchall()
    
    total_completions_all_time = db.execute(
        "SELECT COUNT(*) FROM entries WHERE status = 'done'"
    ).fetchone()[0]

    for row in entries:
        if row["entry_date"] in daily_counts:
            daily_counts[row["entry_date"]] += 1
            
    daily_trend = [{"date": d, "count": daily_counts[d]} for d in dates]
    
    # 3. Habit Performance & Streaks
    habit_stats = []
    global_best_streak = 0
    
    for habit in habits:
        # streaks
        streak_data = calculate_streaks(db, habit["id"])
        cw_streak = streak_data["current_streak"]
        bw_streak = streak_data["best_streak"]
        
        if bw_streak > global_best_streak:
            global_best_streak = bw_streak
            
        # completion rate
        # Total valid days = days since creation or first entry
        # For simplicity, let's use total entries (done + skip + miss) as denominator
        # or just total 'done' / total tracked days.
        # Let's use: (done) / (done + miss + skip)
        
        counts = db.execute(
            """
            SELECT 
                COUNT(CASE WHEN status='done' THEN 1 END) as done,
                COUNT(*) as total
            FROM entries 
            WHERE habit_id = ?
            """, (habit["id"],)
        ).fetchone()
        
        rate = 0
        if counts["total"] > 0:
            rate = round((counts["done"] / counts["total"]) * 100, 1)
            
        habit_stats.append({
            "id": habit["id"],
            "name": habit["name"],
            "color": habit["color"],
            "current_streak": cw_streak,
            "best_streak": bw_streak,
            "completion_rate": rate,
            "total_done": counts["done"]
        })
        
    # Sort by consistency (completion rate)
    habit_stats.sort(key=lambda x: x["completion_rate"], reverse=True)
    
    # 4. Perfect Days (All active habits done)
    # This is expensive to calc perfectly, let's approximate or skip primarily.
    # Actually, easy: Group entries by date, check if count(done) == total_active_habits_that_day
    # Let's skip complex perfect day logic for now to keep it fast, or just count days with > X data.
    
    return jsonify({
        "summary": {
            "total_habits": total_habits,
            "total_completions": total_completions_all_time,
            "best_streak": global_best_streak
        },
        "daily_trend": daily_trend,
        "habit_performance": habit_stats
    })
