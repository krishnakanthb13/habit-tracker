"""
Entry API routes — toggle habit status for a given day.
"""
from flask import Blueprint, request, jsonify
from ..database import get_db
from ..services.day_boundary import get_effective_today

entries_bp = Blueprint("entries", __name__)


def _get_settings_dict(db):
    rows = db.execute("SELECT key, value FROM settings").fetchall()
    return {row["key"]: row["value"] for row in rows}


@entries_bp.route("/entries", methods=["POST"])
def set_entry():
    """
    Create or update an entry for a habit on a specific date.

    Body: { habit_id, date (optional, defaults to today), status: 'done'|'skip'|'miss' }
    Sending the same status again clears the entry (toggle behavior).
    """
    db = get_db()
    data = request.get_json()

    if not data or not data.get("habit_id"):
        return jsonify({"error": "habit_id is required"}), 400

    habit_id = data["habit_id"]
    settings = _get_settings_dict(db)

    # Use provided date or default to effective today
    entry_date = data.get("date") or get_effective_today(settings)
    new_status = data.get("status", "done")

    if new_status and new_status not in ("done", "skip", "miss"):
        return jsonify({"error": "Invalid status"}), 400

    # Ensure empty string is treated as None
    if not new_status:
        new_status = None

    # Check if skip is disabled
    skip_enabled = settings.get("skip_enabled", "true") == "true"
    if new_status == "skip" and not skip_enabled:
        return jsonify({"error": "Skip is disabled"}), 400

    # Check existing entry
    existing = db.execute(
        "SELECT * FROM entries WHERE habit_id = ? AND entry_date = ?",
        (habit_id, entry_date),
    ).fetchone()

    if existing:
        if existing["status"] == new_status or (not existing["status"] and not new_status):
            # Toggle off (setting same status or setting None when already None)
            if existing["note"]:
                # If note exists, set status to NULL but keep entry
                db.execute("UPDATE entries SET status = NULL WHERE id = ?", (existing["id"],))
                db.commit()
                return jsonify({
                    "action": "updated",
                    "habit_id": habit_id,
                    "date": entry_date,
                    "status": None,
                })
            else:
                # No note, acceptable to delete
                db.execute("DELETE FROM entries WHERE id = ?", (existing["id"],))
                db.commit()
                return jsonify({
                    "action": "cleared",
                    "habit_id": habit_id,
                    "date": entry_date,
                    "status": None,
                })
        else:
            # Update to new status (can be None)
            db.execute(
                "UPDATE entries SET status = ? WHERE id = ?",
                (new_status, existing["id"]),
            )
            db.commit()
            return jsonify({
                "action": "updated",
                "habit_id": habit_id,
                "date": entry_date,
                "status": new_status,
            })
    else:
        # Create new entry
        db.execute(
            "INSERT INTO entries (habit_id, entry_date, status) VALUES (?, ?, ?)",
            (habit_id, entry_date, new_status),
        )
        db.commit()
        return jsonify({
            "action": "created",
            "habit_id": habit_id,
            "date": entry_date,
            "status": new_status,
        }), 201


@entries_bp.route("/entries/<int:entry_id>/note", methods=["PUT"])
def update_note(entry_id):
    """Update the note on an existing entry."""
    db = get_db()
    data = request.get_json()

    entry = db.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
    if not entry:
        return jsonify({"error": "Entry not found"}), 404

    note = data.get("note", "").strip()[:1000]

    db.execute(
        "UPDATE entries SET note = ? WHERE id = ?",
        (note, entry_id),
    )
    db.commit()

    return jsonify({"id": entry_id, "note": note})


@entries_bp.route("/entries/note", methods=["PUT"])
def update_note_by_habit_date():
    """Update note by habit_id and date (creates entry if needed)."""
    db = get_db()
    data = request.get_json()
    habit_id = data.get("habit_id")
    settings = _get_settings_dict(db)
    entry_date = data.get("date") or get_effective_today(settings)
    note = data.get("note", "").strip()[:1000]

    existing = db.execute(
        "SELECT * FROM entries WHERE habit_id = ? AND entry_date = ?",
        (habit_id, entry_date),
    ).fetchone()

    if existing:
        db.execute(
            "UPDATE entries SET note = ? WHERE id = ?",
            (note, existing["id"]),
        )
    else:
        # Create a placeholder entry with NO status — just the note
        db.execute(
            "INSERT INTO entries (habit_id, entry_date, status, note) VALUES (?, ?, NULL, ?)",
            (habit_id, entry_date, note),
        )
    db.commit()

    return jsonify({"habit_id": habit_id, "date": entry_date, "note": note})
