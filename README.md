# 🎯 Habit Tracker

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Framework: Flask](https://img.shields.io/badge/framework-Flask-lightgrey.svg)](https://flask.palletsprojects.com/)

A **local-first, cross-platform Habit Tracker Web Application** designed for ultimate data ownership and privacy. Built with Python/Flask and SQLite, it offers a beautiful monthly calendar view, streak analytics, goal setting, and a self-healing database.

> *"The discipline of streaks, without the prison of the cloud."*

![Habit Tracker 1](assets/ht1.png)
![Habit Tracker 2](assets/ht2.png)
![Habit Tracker 3](assets/ht3.png)
![Habit Tracker 4](assets/ht4.png)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
|**Zero-Lag UX**|**Optimistic UI updates** for instant feedback on status toggles and note saving|
|**Three-State Tracking**|✔️ Done · ➖ Skipped · ❌ Missed — cycle through by clicking|
|**Habit reordering**|**Drag & Drop** habit rows to organize your priorities instantly|
|**Monthly Calendar**|Visual table grid with **sticky headers & columns** for seamless scrolling|
|**Archiving (Hide)**|Clean up your view by **Hiding** old habits while keeping all their historical data|
|**Squirky UI**|Modern, organic rounded aesthetic with optimized **Glassmorphism** for speed|
|**Tactile Controls**|Custom number spinners and segmented buttons replace native browser inputs|
|**Streak Analytics**|Current streak 🔥, best streak ⭐, total completions per habit|
| **Goal Period Tracking** | Set daily, weekly, or custom frequency goals |
| **Interactive Analytics** | Modern dashboard with activity trends, habit consistency charts, and detailed performance metrics |
| **5 Themes** | Light, Dark, Pure Dark (OLED), Ocean, Sunset |
| **🌙 Day Extension** | Late-night tracker? Extend your day boundary past midnight. (configurable up to 6 AM) |
| **Skip Status** | Enable/disable skipped-day status (marked as `➖`, doesn't break streaks) |
| **Notes** | Right-click any calendar cell to add/clear notes with **background sync** |
| **Party Popper** | 🎉 Confetti physics celebration on habit completion (toggleable) |
| **Import/Export** | Full CSV export (ZIP) and import with preview for easy backups |
| **Self-Healing DB** | Integrity checks, robust auto-backups, and repair with `.corrupt` safety |
| **Test Suite** | Comprehensive unit tests for streak logic and API stability |
| **Keyboard Shortcuts** | `Ctrl+N` for new habits, `Esc` to close dialogs |

---

## 🚀 Quick Start

### Windows
```batch
Double-click launch.bat
```

### Linux / macOS
```bash
chmod +x launch.sh
./launch.sh
```

**The launcher handles everything:**
1. Verifies Python 3.10+
2. Uses global packages if present, otherwise creates a `venv`
3. Installs dependencies from `requirements.txt`
4. Launches the app at `http://localhost:5000`

---

## 🛠 Tech Stack

- **Backend**: Python 3.10+ / Flask (Thin wrapper around business logic)
- **Database**: SQLite 3 (WAL mode for concurrency and reliability)
- **Frontend**: Vanilla JS (ES6) + CSS Variables + Custom Tactile Controls (Zero JS framework dependencies)
- **Templating**: Jinja2 (Serverside rendering for initial load speed)

**No cloud accounts. No subscriptions. Works fully offline.**

---

## 📁 Project Structure

```text
habit-tracker/
├── app/                    # Main Flask application
├── database/               # Local SQLite storage & backups
├── tests/                  # API and streak engine test suite
├── launch.bat              # One-click Windows launcher
├── launch.sh               # One-click Unix launcher
├── requirements.txt        # Flask and dependencies
├── run.py                  # Entry Point script
├── CODE_DOCUMENTATION.md   # Technical deep-dive
├── API_DOCUMENTATION.md    # REST API Endpoint details
├── SECURITY.md             # Security audit & standards report
├── DESIGN_PHILOSOPHY.md     # Why it was built this way
├── CONTRIBUTING.md         # How to help
└── LICENSE                 # GNU GPL v3
```

---

## 🤖 API & Logic

- **Streak Calculation**: `Done` increments, `Missed` (or empty) breaks, `Skipped` is transparent (skipped days are ignored in the chain).
- **Day Boundary**: Controlled by `day_extension` setting. If enabled, the "effective today" shifts based on your cutoff hour (e.g., 3 AM).
- **Goal Engine**: Evaluates progress based on the current period (Week/Custom Day Range).

---

## License

Copyright (C) 2026 **Krishna Kanth B** (`krishnakanthb13`)

This project is open-source software and is licensed under the **GNU GPL v3**. See the [LICENSE](LICENSE) file for more details.

---
