"""
Database connection manager and migration engine.
"""
import os
import sqlite3
from flask import g, current_app

SCHEMA_VERSION = 1


def get_db():
    """Get a database connection for the current request context."""
    if "db" not in g:
        db_path = current_app.config["DATABASE_PATH"]
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db


def close_db(e=None):
    """Close the database connection at end of request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    """Initialize database with schema and run migrations."""
    db_path = app.config["DATABASE_PATH"]
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    # Check if schema_version table exists
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'"
    )
    if cursor.fetchone() is None:
        # Fresh database — apply full schema
        _apply_schema(conn)
    else:
        # Existing database — run migrations
        _run_migrations(conn)

    conn.close()
    app.teardown_appcontext(close_db)


def _apply_schema(conn):
    """Apply the full initial schema."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS habits (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            description TEXT DEFAULT '',
            color       TEXT DEFAULT '#4CAF50',
            position    INTEGER DEFAULT 0,
            created_at  TEXT DEFAULT (datetime('now')),
            archived    INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS entries (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id    INTEGER NOT NULL REFERENCES habits(id) ON DELETE CASCADE,
            entry_date  TEXT NOT NULL,
            status      TEXT NOT NULL CHECK(status IN ('done', 'skip', 'miss')),
            note        TEXT DEFAULT '',
            created_at  TEXT DEFAULT (datetime('now')),
            UNIQUE(habit_id, entry_date)
        );

        CREATE TABLE IF NOT EXISTS goals (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id    INTEGER NOT NULL UNIQUE REFERENCES habits(id) ON DELETE CASCADE,
            goal_type   TEXT NOT NULL CHECK(goal_type IN ('daily', 'weekly', 'custom')),
            target      INTEGER NOT NULL DEFAULT 1,
            period_days INTEGER DEFAULT 7
        );

        CREATE TABLE IF NOT EXISTS settings (
            key         TEXT PRIMARY KEY,
            value       TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS schema_version (
            version     INTEGER PRIMARY KEY,
            applied_at  TEXT DEFAULT (datetime('now'))
        );

        -- Indexes
        CREATE INDEX IF NOT EXISTS idx_entries_habit_date ON entries(habit_id, entry_date);
        CREATE INDEX IF NOT EXISTS idx_entries_date ON entries(entry_date);
        CREATE INDEX IF NOT EXISTS idx_habits_position ON habits(position);

        -- Default settings
        INSERT OR IGNORE INTO settings (key, value) VALUES ('theme', 'dark');
        INSERT OR IGNORE INTO settings (key, value) VALUES ('day_extension', 'false');
        INSERT OR IGNORE INTO settings (key, value) VALUES ('day_extension_hour', '3');
        INSERT OR IGNORE INTO settings (key, value) VALUES ('skip_enabled', 'true');
        INSERT OR IGNORE INTO settings (key, value) VALUES ('animations_enabled', 'true');

        -- Record schema version
        INSERT OR IGNORE INTO schema_version (version) VALUES (1);
    """)
    conn.commit()


def _run_migrations(conn):
    """Run any pending migrations."""
    cursor = conn.execute("SELECT MAX(version) FROM schema_version")
    current_version = cursor.fetchone()[0] or 0

    # Add future migrations here as:
    # if current_version < 2:
    #     conn.executescript("ALTER TABLE ...")
    #     conn.execute("INSERT INTO schema_version (version) VALUES (2)")
    #     conn.commit()

    pass
