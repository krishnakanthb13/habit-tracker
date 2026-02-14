Base Prompt

- habit tracker web application
- Options loop - tick ✔, skip -, missed ❌
- dark mode and light mode - also pure dark theme - also add more themes if you can
- monthly calendar with ability to add habits and notes
- data saved in sql lite
- able to export and import data as csv, with all details
- toggle option to extend day a few hours past midnight upto 3am
- toggle option to enable and disable the skipped days
- highlight todays date
- show total and highest streak at the end of each habit
- also should be able to set goals for each habit
- toggle to enable and disable animation - party popper animation when habit is completed
- option to repair or self heal database in case of any corruption
- add some sub-context to each option, like a readme kinda - contains why and when to use it
- should support windows, linux and mac os, so create bat and sh files respectively to launch it
- make it use the global packages, if not avaliable the create a environment and install the packages in them
- reference: https://app.dailyhabits.xyz/ and https://github.com/iSoron/uhabits

---

## ✅ MASTER PROMPT — Build a Cross-Platform Habit Tracker Web Application

You are a **Senior Full-Stack Software Architect and Developer** tasked with designing and implementing a **production-ready Habit Tracker Web Application** inspired by:

* [https://app.dailyhabits.xyz/](https://app.dailyhabits.xyz/)
* [https://github.com/iSoron/uhabits](https://github.com/iSoron/uhabits)

Your goal is to design, architect, and implement the entire project with clean structure, maintainability, cross-platform support, and long-term reliability.

---

# 1️⃣ ROLE & ENGINEERING STANDARD

Act as:

* Senior Full-Stack Engineer
* DevOps-aware architect
* UI/UX-conscious frontend developer
* SQLite database reliability specialist

Follow:

* Clean Architecture principles
* Modular structure
* Separation of concerns
* Defensive programming
* Clear documentation
* Production-ready code (not prototype code)

---

# 2️⃣ CORE FEATURE SET

## A. Habit Tracking System

Each habit must support:

* Status loop:
  * ✔ Completed
  * - Skipped
  * ❌ Missed
* Optional ability to **disable skipped days**
* Monthly calendar view
* Highlight today's date
* Add habits dynamically
* Add notes per day per habit
* Show:
  * Current streak
  * Total streak
  * Highest streak
* Set goals per habit:
  * Daily
  * X times per week
  * Custom target logic

---

## B. Day Extension Feature

Add toggle:

* Extend “day boundary” up to 3AM
* Example:
  * If enabled at 2:30 AM → counts as previous day
* Must be:
  * Globally configurable
  * Applied consistently across streak calculations

---

## C. Themes & UI System

Implement:

* Light mode
* Dark mode
* Pure dark (true black)
* At least 2 additional creative themes
* Theme persistence

Add:
* Toggle for animations
* Party popper animation when habit is completed
* Ability to disable animations entirely

---

## D. Calendar System

Monthly calendar must:
* Show habit state visually
* Display markers:
  * ✔
  * -
  * ❌
* Allow adding notes directly
* Highlight today
* Allow navigation across months

---

## E. Database System

Use:
* SQLite (local storage backend)

Requirements:
* Schema design explanation
* Normalized structure
* Foreign key usage
* Index optimization

Must include:
* Auto-migration system
* Database repair/self-heal mechanism:
  * Integrity check
  * Rebuild corrupted tables if possible
  * Backup before repair

---

## F. Import / Export

Must support:

* Export to CSV:
  * All habits
  * All daily entries
  * Notes
  * Streak data
  * Goals
* Import from CSV
  * Validate structure
  * Graceful error handling
  * Preview before commit

---

## G. Sub-Context Documentation System

For each major feature, include:

* Description
* Why it exists
* When to use it
* Edge cases
* Configuration notes

Generate a built-in “Readme / Help” panel in the UI.

---

## H. Cross-Platform Support

Must run on:

* Windows
* Linux
* macOS

Provide:

* .bat launcher
* .sh launcher

Launcher logic:

1. Check for required global packages
2. If missing:

   * Create virtual environment
   * Install required dependencies
3. Start application

No Docker required unless justified.

---

# 3️⃣ TECH STACK REQUIREMENTS

You must:

1. Propose the optimal stack
2. Justify why chosen
3. Ensure SQLite compatibility
4. Ensure cross-platform compatibility

Example acceptable stacks:

* Python + FastAPI + Jinja + Vanilla JS
* Node + Express + SQLite

Keep it lightweight.

---

# 4️⃣ ARCHITECTURE DESIGN

You must produce:

1. Full folder structure
2. Database schema
3. API routes
4. UI components breakdown
5. State management explanation
6. Streak calculation algorithm
7. Goal evaluation algorithm
8. Day-boundary override logic
9. Repair/self-heal logic

---

# 5️⃣ STREAK LOGIC SPECIFICATION

You must define clearly:

* What counts toward streak?
* How skipped days affect streak?
* How disabled skipped toggle changes logic?
* How weekly goals affect streak?
* How day extension affects streak?

Provide clear pseudo-code.

---

# 6️⃣ ERROR HANDLING REQUIREMENTS

System must handle:

* Corrupted DB
* Partial CSV import
* Invalid dates
* Timezone mismatch
* Toggle conflicts
* Missing fields
* Race conditions

Provide strategies.

---

# 7️⃣ OUTPUT FORMAT

Deliver:

1. Architecture overview
2. Stack justification
3. Folder structure
4. Database schema (SQL)
5. Core backend code
6. Core frontend structure
7. Launcher scripts (.bat + .sh)
8. Import/export logic
9. Streak algorithm pseudo-code
10. Database repair mechanism
11. Theming system
12. Built-in help documentation content
13. Deployment instructions

Code must be:

* Structured
* Commented
* Clean
* Modular
* Production-grade

---

# 8️⃣ CONSTRAINTS

* Must be lightweight
* No unnecessary dependencies
* Must work offline
* Must not require cloud
* Must persist data safely
* Must recover from failures

---

# 9️⃣ PERFORMANCE & UX

* Smooth calendar navigation
* Minimal load time
* Efficient SQLite queries
* Animation must not block UI
* Dark mode optimized for OLED (pure dark)

---

# 🔟 FINAL OBJECTIVE

Produce a **fully buildable, cross-platform, self-healing, extensible Habit Tracker Web Application** with robust architecture and long-term maintainability.

The result should be something that:

* Can scale
* Can be extended
* Can be maintained by another developer
* Feels polished
* Is reliable under failure conditions

---

Deliver with precision.
No placeholders.
No pseudo-project.
This should be production-ready.
