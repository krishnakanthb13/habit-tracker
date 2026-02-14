# Habit Tracker API Documentation

This document provides a comprehensive overview of the Habit Tracker backend API.

## Base URL
The API is typically served at `http://localhost:5000/api` (unless configured otherwise).

---

## 1. Habits API
Endpoints for managing habits.

### `GET /habits`
**Description**: Lists all active (non-archived) habits with their current statistics, including streaks and goal progress.
**Response**: `200 OK`
```json
[
  {
    "best_streak": 5,
    "color": "#4CAF50",
    "created_at": "2026-02-14 12:00:00",
    "current_streak": 3,
    "description": "Daily exercise",
    "goal": { ... },
    "id": 1,
    "name": "Exercise",
    "position": 0,
    "today_note": "Morning run",
    "today_status": "done",
    "total_done": 20
  }
]
```

### `POST /habits`
**Description**: Creates a new habit.
**Request Body**:
- `name` (string, **required**)
- `description` (string, optional)
- `color` (string, optional)
**Response**: `201 Created`

### `PUT /habits/<habit_id>`
**Description**: Updates an existing habit's details.
**Request Body**:
- `name` (string, optional)
- `description` (string, optional)
- `color` (string, optional)
- `position` (integer, optional)
**Response**: `200 OK`

### `DELETE /habits/<habit_id>`
**Description**: Archives a habit (soft delete).
**Response**: `200 OK`

### `PUT /habits/reorder`
**Description**: Reorders habits based on a provided list of IDs.
**Request Body**:
- `order` (array of integers, **required**): List of habit IDs in the desired order.
**Response**: `200 OK`

---

## 2. Entries API
Endpoints for recording habit status and notes.

### `POST /entries`
**Description**: Sets or toggles the status of a habit for a specific date. If the same status is sent for an existing entry, it toggles it off (clears or nullifies).
**Request Body**:
- `habit_id` (integer, **required**)
- `status` (string): One of `"done"`, `"skip"`, `"miss"`, or `null`.
- `date` (string, optional): Format `YYYY-MM-DD`. Defaults to effective today.
**Response**: `200 OK` or `201 Created`

### `PUT /entries/<entry_id>/note`
**Description**: Updates the note for a specific entry.
**Request Body**:
- `note` (string, **required**)
**Response**: `200 OK`

### `PUT /entries/note`
**Description**: Updates or creates a note for a habit on a specific date.
**Request Body**:
- `habit_id` (integer, **required**)
- `note` (string, **required**)
- `date` (string, optional): Format `YYYY-MM-DD`.
**Response**: `200 OK`

---

## 3. Calendar API
Endpoints for retrieving data for calendar views.

### `GET /calendar`
**Description**: Retrieves habit entries and layout data for a specific month.
**Query Parameters**:
- `month` (string): Format `YYYY-MM` (e.g., `2026-02`). Defaults to current month.
**Response**: `200 OK`
```json
{
  "days_in_month": 28,
  "first_weekday": 5,
  "habits": [
    {
      "color": "#4CAF50",
      "entries": {
        "2026-02-14": { "id": 123, "status": "done", "note": "..." }
      },
      "id": 1,
      "name": "Exercise"
    }
  ],
  "month": 2,
  "month_name": "February",
  "today": "2026-02-14",
  "year": 2026
}
```

---

## 4. Goals API
Endpoints for managing habit goals.

### `GET /habits/<habit_id>/goals`
**Description**: Retrieves goal configuration and current progress for a habit.
**Response**: `200 OK`

### `POST /habits/<habit_id>/goals`
**Description**: Sets or updates a goal for a habit.
**Request Body**:
- `goal_type` (string, **required**): One of `"daily"`, `"weekly"`, `"custom"`.
- `target` (integer, **required**): Target count (e.g., 5 times).
- `period_days` (integer, optional): Period for custom goals. Defaults to 7 for weekly.
**Response**: `201 Created`

### `DELETE /habits/<habit_id>/goals`
**Description**: Removes the goal for a habit.
**Response**: `200 OK`

---

## 5. Settings API
Endpoints for user preferences.

### `GET /settings`
**Description**: Retrieves all application settings.
**Response**: `200 OK`

### `PUT /settings`
**Description**: Updates one or more application settings.
**Request Body**: A dictionary of key-value pairs. Valid keys include:
- `theme`
- `day_extension`
- `day_extension_hour`
- `skip_enabled`
- `animations_enabled`
**Response**: `200 OK`

---

## 6. Data API
Endpoints for importing and exporting habit data.

### `GET /export`
**Description**: Exports all data as a ZIP file containing CSVs for habits, entries, goals, and settings.
**Response**: `200 OK` (Zip Archive)

### `POST /import/preview`
**Description**: Previews a CSV file before importing.
**Request Body**: Multipart Form Data with a `file` field.
**Response**: `200 OK` (JSON preview)

### `POST /import`
**Description**: Imports data from a CSV file into a specific table.
**Request Body**: Multipart Form Data:
- `file`: The CSV file.
- `table_name`: One of `"habits"`, `"entries"`, `"goals"`, `"settings"`.
**Response**: `200 OK`

---

## 7. Health API
Endpoints for database maintenance.

### `GET /health`
**Description**: Runs an integrity check on the SQLite database.
**Response**: `200 OK` (or `500 Internal Server Error` if check fails)

### `POST /health/backup`
**Description**: Creates a manual backup of the database file.
**Response**: `200 OK`

### `POST /health/repair`
**Description**: Attempts to repair a corrupted database.
**Response**: `200 OK`

---

## 8. Analytics API
Endpoints for data visualization and trends.

### `GET /analytics`
**Description**: Retrieves aggregated analytics data, including 30-day activity trends and habit consistency ranking.
**Response**: `200 OK`
```json
{
  "summary": { "total_habits": 5, "total_completions": 150, "best_streak": 20 },
  "daily_trend": [ { "date": "2026-02-14", "count": 3 }, ... ],
  "habit_performance": [ { "name": "Exercise", "completion_rate": 95, "current_streak": 5, ... }, ... ]
}
```

---

## 9. Page Routes
These routes serve the HTML frontend.

### `GET /`
**Description**: Serves the main Habit Tracker dashboard (`index.html`).

### `GET /help`
**Description**: Serves the help and documentation page (`help.html`).

### `GET /analytics`
**Description**: Serves the interactive analytics dashboard (`analytics.html`).
