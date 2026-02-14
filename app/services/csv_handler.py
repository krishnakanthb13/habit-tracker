"""
CSV import/export handler.
"""
import csv
import io
import zipfile
from datetime import datetime


def export_all_data(db):
    """
    Export all habits, entries, goals, and settings as CSV files in a zip archive.

    Returns:
        bytes: zip file content
    """
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        # Habits
        rows = db.execute(
            "SELECT id, name, description, color, position, created_at, archived FROM habits"
        ).fetchall()
        zf.writestr("habits.csv", _rows_to_csv(rows, [
            "id", "name", "description", "color", "position", "created_at", "archived"
        ]))

        # Entries
        rows = db.execute(
            "SELECT id, habit_id, entry_date, status, note, created_at FROM entries"
        ).fetchall()
        zf.writestr("entries.csv", _rows_to_csv(rows, [
            "id", "habit_id", "entry_date", "status", "note", "created_at"
        ]))

        # Goals
        rows = db.execute(
            "SELECT id, habit_id, goal_type, target, period_days FROM goals"
        ).fetchall()
        zf.writestr("goals.csv", _rows_to_csv(rows, [
            "id", "habit_id", "goal_type", "target", "period_days"
        ]))

        # Settings
        rows = db.execute("SELECT key, value FROM settings").fetchall()
        zf.writestr("settings.csv", _rows_to_csv(rows, ["key", "value"]))

    buffer.seek(0)
    return buffer.getvalue()


def preview_import(file_storage):
    """
    Parse an uploaded CSV file and return a preview of its contents.

    Args:
        file_storage: Flask FileStorage object

    Returns:
        dict with 'filename', 'headers', 'row_count', 'sample_rows', 'valid', 'errors'
    """
    try:
        content = file_storage.read().decode("utf-8-sig")
        file_storage.seek(0)

        reader = csv.DictReader(io.StringIO(content))
        headers = reader.fieldnames or []
        rows = list(reader)

        # Determine which table this CSV corresponds to
        table, errors = _identify_table(headers)

        return {
            "filename": file_storage.filename,
            "headers": headers,
            "row_count": len(rows),
            "sample_rows": rows[:5],
            "table": table,
            "valid": len(errors) == 0,
            "errors": errors,
        }
    except Exception as e:
        return {
            "filename": getattr(file_storage, "filename", "unknown"),
            "headers": [],
            "row_count": 0,
            "sample_rows": [],
            "table": None,
            "valid": False,
            "errors": [str(e)],
        }


def import_csv(db, file_content, table_name):
    """
    Import CSV data into the specified table.

    Args:
        db: database connection
        file_content: str, CSV content
        table_name: str, one of 'habits', 'entries', 'goals', 'settings'

    Returns:
        dict with 'imported' count and any 'errors'
    """
    reader = csv.DictReader(io.StringIO(file_content))
    imported = 0
    errors = []

    for i, row in enumerate(reader, 1):
        try:
            if table_name == "habits":
                db.execute(
                    "INSERT OR REPLACE INTO habits (id, name, description, color, position, created_at, archived) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (row.get("id"), row["name"], row.get("description", ""),
                     row.get("color", "#4CAF50"), row.get("position", 0),
                     row.get("created_at", datetime.now().isoformat()),
                     row.get("archived", 0)),
                )
            elif table_name == "entries":
                _validate_entry(row)
                db.execute(
                    "INSERT OR REPLACE INTO entries (habit_id, entry_date, status, note) "
                    "VALUES (?, ?, ?, ?)",
                    (row["habit_id"], row["entry_date"], row["status"],
                     row.get("note", "")),
                )
            elif table_name == "goals":
                db.execute(
                    "INSERT OR REPLACE INTO goals (habit_id, goal_type, target, period_days) "
                    "VALUES (?, ?, ?, ?)",
                    (row["habit_id"], row["goal_type"],
                     row.get("target", 1), row.get("period_days", 7)),
                )
            elif table_name == "settings":
                db.execute(
                    "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                    (row["key"], row["value"]),
                )
            imported += 1
        except Exception as e:
            errors.append(f"Row {i}: {str(e)}")

    db.commit()
    return {"imported": imported, "errors": errors}


def _rows_to_csv(rows, headers):
    """Convert SQLite rows to CSV string."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for row in rows:
        writer.writerow([row[h] for h in headers])
    return output.getvalue()


def _identify_table(headers):
    """Identify which table a CSV corresponds to based on its headers."""
    headers_set = set(h.lower() for h in headers)
    errors = []

    if {"name", "description", "color"}.issubset(headers_set):
        return "habits", errors
    elif {"habit_id", "entry_date", "status"}.issubset(headers_set):
        return "entries", errors
    elif {"habit_id", "goal_type", "target"}.issubset(headers_set):
        return "goals", errors
    elif {"key", "value"}.issubset(headers_set):
        return "settings", errors
    else:
        errors.append(f"Cannot identify table from headers: {headers}")
        return None, errors


def _validate_entry(row):
    """Validate an entry row before import."""
    if "habit_id" not in row or not row["habit_id"]:
        raise ValueError("Missing habit_id")
    if "entry_date" not in row or not row["entry_date"]:
        raise ValueError("Missing entry_date")
    if "status" not in row or row["status"] not in ("done", "skip", "miss"):
        raise ValueError(f"Invalid status: {row.get('status')}")
    # Validate date format
    try:
        datetime.strptime(row["entry_date"], "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid date format: {row['entry_date']}")
