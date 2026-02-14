# Habit Tracker - Code Documentation

This document provides a technical overview of the Habit Tracker codebase, its architecture, and data flow. For a detailed list of available API endpoints, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md).

## 1. File & Folder Structure

```text
habit-tracker/
├── app/                    # Main Flask application
│   ├── routes/             # API Endpoints (Blueprints)
│   │   ├── analytics.py    # **Aggregated trend & performance data**
│   │   ├── calendar.py     # Month-view data aggregation
│   │   ├── data.py         # CSV Import/Export
│   │   ├── entries.py      # Habit status toggling & notes
│   │   ├── goals_routes.py # Goal CRUD
│   │   ├── habits.py       # Habit CRUD
│   │   ├── health.py       # DB integrity & repair
│   │   ├── pages.py        # Static page serving (Dashboard/Help/Analytics)
│   │   └── settings.py     # App settings persistence
│   ├── services/           # Business Logic
│   │   ├── csv_handler.py   # ZIP/CSV packaging & parsing
│   │   ├── day_boundary.py  # Logic for late-night extensions
│   │   ├── db_repair.py     # SQLite dump/reimport recovery
│   │   ├── goals.py         # Progress evaluation engine
│   │   └── streak.py        # Algorithmic streak calculation
│   ├── static/             # Frontend Assets
│   │   ├── css/            # base.css, themes.css, animations.css
│   │   ├── js/             # analytics.js, api.js, calendar.js, habits.js, etc.
│   │   └── img/            # favicon.svg
│   ├── templates/          # Jinja2 Templates (index.html, help.html)
│   ├── __init__.py         # App factory & Blueprint registration
│   ├── config.py           # Path & Port configuration
│   └── database.py         # SQLite connection & migration engine
├── database/               # Local SQLite storage (Gitignored)
├── tests/                  # Test Suite
│   ├── test_smoke.py       # API stability & health tests
│   └── test_streak.py      # Streak engine unit tests
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
| `csv_handler.py` | ZIP based data portability | `export_to_zip()`, `import_from_csv()` |
| `db_repair.py` | Self-healing DB mechanism | `repair_database()` - Now moves corrupt files to `.corrupt` extension. |

### 4. Data Flow

1.  **Status Toggle (Optimistic)**: User clicks a cell -> `calendar.js` immediately updates DOM (classes, symbols, counts) -> `API.post('/api/entries')` fires in background -> Errors trigger a fallback re-render.
2.  **Habit Reordering**: `SortableJS` management in `calendar.js` -> `PUT /api/habits/reorder` -> Updates `display_order` column for persistent priorities.
3.  **Note Management**: Saving a note triggers an optimistic "note dot" (📝) update in the UI while the JSON payload syncs with `entries.py`.
4.  **Parallelized Boot**: `app.js` uses `Promise.all()` to load settings, habits, and calendar data simultaneously, cutting initial load time by ~50%.

## 5. Execution Flow

1.  **Launch**: `run.py` starts -> `create_app()` initializes -> `database.py:init_db()` runs migrations.
2.  **Frontend Boot**: `index.html` loads -> `app.js` initializes modules -> `ThemeManager` applies CSS vars -> **Parallel fetch** of Month and Settings data.
3.  **Active Sessions**: User interacts with the calendar; JS pulses the UI and plays confetti animations on habit completion without page reloads.

## 6. Dependencies

-   **Runtime**: Python 3.10+, `Flask==3.1.0`.
-   **Frontend**: Modern Browser (ES6+ support required), `SortableJS` (for reordering), `Lucide` (templated icons).
-   **Environment**: Cross-platform (Windows/Linux/macOS).

## 7. Performance Considerations

The Habit Tracker is optimized for low-resource local environments:

1.  **Optimistic UI Engine**: All critical user actions (cycling status, saving notes, unhiding habits) trigger local DOM updates *before* the network request completes, eliminating perceived latency.
2.  **GPU-Optimized Glassmorphism**: High-cost CSS filters like `backdrop-filter: blur()` are limited to 8-16px and pinned to separate GPU layers using `will-change: transform`.
3.  **Paint Containment**: Modals and side panels use `contain: paint` to limit the scope of browser reflows during animations.
4.  **Scoped Icon Rendering**: Lucide icon generation is scoped to specific containers (e.g., just the table body) to prevent expensive full-document DOM scans.
5.  **SQLite WAL Mode**: The database operates in Write-Ahead Logging mode (`PRAGMA journal_mode=WAL`), allowing concurrent readers/writers.
6.  **Index Optimization**: Composite indexes on `(habit_id, entry_date)` ensure O(log N) lookup speeds for even the densest habit histories.

## 8. Progressive Web App (PWA) Architecture

The application implements a "stale-while-revalidate" caching strategy via a Service Worker (`service-worker.js`) to ensure instant load times and offline availability.

1.  **App Shell Model**: Core assets (CSS, JS, Fonts, Icons) are precached during the `install` phase of the Service Worker.
2.  **Manifest Integration**: A `manifest.json` file is served from the root to define the app's name, theme colors (`#0f172a`), and display mode (`standalone`), allowing it to pass PWA installability criteria.
3.  **Offline Fallback**: While the initial HTML is network-first, cached assets ensure the UI skeleton renders immediately even without a connection.

