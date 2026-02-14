# Habit Tracker - Code Documentation

This document provides a technical overview of the Habit Tracker codebase, its architecture, and data flow.

## 1. File & Folder Structure

```text
habit-tracker/
├── app/                    # Main Flask application
│   ├── routes/             # API Endpoints (Blueprints)
│   │   ├── calendar.py     # Month-view data aggregation
│   │   ├── data.py         # CSV Import/Export
│   │   ├── entries.py      # Habit status toggling & notes
│   │   ├── goals_routes.py # Goal CRUD
│   │   ├── habits.py       # Habit CRUD
│   │   ├── health.py       # DB integrity & repair
│   │   ├── pages.py        # Static page serving (Dashboard/Help)
│   │   └── settings.py     # App settings persistence
│   ├── services/           # Business Logic
│   │   ├── csv_handler.py   # ZIP/CSV packaging & parsing
│   │   ├── day_boundary.py  # Logic for late-night extensions
│   │   ├── db_repair.py     # SQLite dump/reimport recovery
│   │   ├── goals.py         # Progress evaluation engine
│   │   └── streak.py        # Algorithmic streak calculation
│   ├── static/             # Frontend Assets
│   │   ├── css/            # base.css, themes.css, animations.css
│   │   ├── js/             # api.js, calendar.js, habits.js, etc.
│   │   └── img/            # favicon.svg
│   ├── templates/          # Jinja2 Templates (index.html, help.html)
│   ├── __init__.py         # App factory & Blueprint registration
│   ├── config.py           # Path & Port configuration
│   └── database.py         # SQLite connection & migration engine
├── database/               # Local SQLite storage (Gitignored)
├── launch.bat              # Windows Launcher
├── launch.sh               # Linux/macOS Launcher
├── run.py                  # Entry Point script
├── requirements.txt        # Python dependencies
└── LICENSE                 # GPL v3 License
```

## 2. High-Level Architecture

The application follows a **Modular Monolith** pattern using Flask Blueprints. It is designed to be **strictly local-first**, meaning no external APIs, cloud storage, or internet connection is required after initial setup.

-   **Backend**: Python/Flask handles routing, data validation, and complex streak/goal calculations.
-   **Frontend**: A Single-page Application (SPA) feel built with Vanilla JavaScript, communicating via a REST-like API.
-   **Database**: SQLite with WAL (Write-Ahead Logging) for reliable local storage and integrity.

## 3. Core Modules

| Module | Purpose | Key Function |
| :--- | :--- | :--- |
| `streak.py` | Calculates current/best streaks | `calculate_streaks()` |
| `goals.py` | Evaluates daily/weekly/custom goals | `evaluate_goal()` |
| `day_boundary.py` | Handles "cutoff hour" extensions | `get_effective_date()` |
| `csv_handler.py` | ZIP based data portable | `export_to_zip()`, `import_from_csv()` |
| `db_repair.py` | Self-healing database mechanism | `repair_database()` |

## 4. Data Flow

```mermaid
graph TD
    User((User)) -->|Browser| UI[Vanilla JS Frontend]
    UI -->|JSON/Fetch| API[Flask API Routes]
    API -->|Validation| Services[Business Logic Services]
    Services -->|SQL| DB[(SQLite Database)]
    DB -->|Results| Services
    Services -->|Calculated Data| API
    API -->|JSON Response| UI
```

1.  **Status Toggle**: User clicks a cell -> `calendar.js` -> `API.post('/api/entries')` -> `entries.py` -> `streak.py` updates stats -> Response returns updated UI state.
2.  **Date Logic**: All entries use `day_boundary.py` to determine if a 2 AM action belongs to "Today" or "Yesterday" based on user settings.

## 5. Execution Flow

1.  **Launch**: `run.py` starts -> `create_app()` initializes -> `database.py:init_db()` runs migrations.
2.  **Frontend Boot**: `index.html` loads -> `app.js` initializes modules -> `ThemeManager` applies CSS vars -> `Calendar.load()` fetches initial month view.
3.  **Active Sessions**: User interacts with the calendar; JS pulses the UI and plays confetti animations on habit completion without page reloads.

## 6. Dependencies

-   **Runtime**: Python 3.10+, `Flask==3.1.0`.
-   **Frontend**: Modern Browser (ES6+ support required).
-   **Environment**: Cross-platform (Windows/Linux/macOS).
```
