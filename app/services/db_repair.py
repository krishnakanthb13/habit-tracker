"""
Database repair / self-heal service.
"""
import os
import shutil
import sqlite3
from datetime import datetime


def integrity_check(db_path):
    """
    Run PRAGMA integrity_check on the database.

    Returns:
        dict with 'ok' (bool) and 'details' (list of strings)
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.execute("PRAGMA integrity_check")
        results = [row[0] for row in cursor.fetchall()]
        ok = len(results) == 1 and results[0] == "ok"
        return {"ok": ok, "details": results}
    except Exception as e:
        return {"ok": False, "details": [str(e)]}
    finally:
        if conn:
            conn.close()


def create_backup(db_path, backup_dir):
    """
    Create a timestamped backup of the database.

    Returns:
        str: path to backup file
    """
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"habits_backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_filename)
    shutil.copy2(db_path, backup_path)
    return backup_path


def repair_database(db_path, backup_dir):
    """
    Attempt to repair a corrupted database.

    Steps:
    1. Create backup
    2. Attempt recovery via dump/reimport
    3. Verify foreign key constraints

    Returns:
        dict with 'success' (bool), 'backup_path' (str), 'details' (list)
    """
    details = []

    # Step 1: Backup
    try:
        backup_path = create_backup(db_path, backup_dir)
        details.append(f"Backup created: {os.path.basename(backup_path)}")
    except Exception as e:
        return {
            "success": False,
            "backup_path": None,
            "details": [f"Backup failed: {str(e)}"],
        }

    # Step 2: Attempt dump and reimport
    try:
        # Export all data
        old_conn = sqlite3.connect(db_path)
        dump = list(old_conn.iterdump())
        old_conn.close()
        details.append(f"Exported {len(dump)} SQL statements")

        # Recreate database
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        corrupt_path = f"{db_path}.corrupt_{timestamp}"
        shutil.move(db_path, corrupt_path)
        details.append(f"Moved corrupted DB to: {os.path.basename(corrupt_path)}")
        
        new_conn = sqlite3.connect(db_path)
        new_conn.executescript("\n".join(dump))
        new_conn.close()
        details.append("Database rebuilt from dump")

    except Exception as e:
        # If dump fails, restore from backup
        details.append(f"Dump/rebuild failed: {str(e)}")
        try:
            shutil.copy2(backup_path, db_path)
            details.append("Restored from backup")
        except Exception as e2:
            details.append(f"Restore also failed: {str(e2)}")
        return {"success": False, "backup_path": backup_path, "details": details}

    # Step 3: Verify foreign keys
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys=ON")
        fk_check = conn.execute("PRAGMA foreign_key_check").fetchall()
        conn.close()

        if fk_check:
            details.append(f"Foreign key violations found: {len(fk_check)}")
        else:
            details.append("Foreign key check passed")
    except Exception as e:
        details.append(f"FK check error: {str(e)}")

    # Final integrity check
    final_check = integrity_check(db_path)
    details.append(
        f"Final integrity: {'PASS' if final_check['ok'] else 'FAIL'}"
    )

    return {
        "success": final_check["ok"],
        "backup_path": backup_path,
        "details": details,
    }
