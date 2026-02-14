# Habit Tracker - Design Philosophy

## 1. Problem Definition

Most habit trackers today are cloud-dependent, ad-supported, or require subscriptions. This creates friction:
- **Privacy**: Your daily habits and notes are stored on someone else's server.
- **Ownership**: If the service shuts down, your data is lost.
- **Latency**: Cloud sync can lag in low-connectivity areas.

## 2. Why this solution?

The Habit Tracker was built to be **truly yours**. It is a local-first web application that bridges the gap between the power of a desktop app and the accessibility of a web dashboard.

## 3. Design Principles

- **Local-First & Privacy**: Data never leaves your machine. SQLite is used for high-performance, single-user storage.
- **Zero-Lag UX (Optimistic UI)**: We prioritize perceived performance. By updating the UI immediately and syncing in the background, we remove the friction of waiting for database writes, making the app feel like a native desktop tool.
- **Squirky Aesthetic**: A "modern organic" look utilizing super-ellipses (squircles), gentle glassmorphism, and a refined color palette that scales across 5 premium themes.
- **Tactile Inputs**: We replace standard browser inputs (dropdowns, number spinners) with custom, touch-friendly segment buttons and controls that feel physical and responsive. 
- **Data-Positive Deletion (Hide vs. Delete)**: We encourage "Hiding" habits rather than deleting them. This preserves historical data and streaks while keeping the current view clean.
- **Zero Configuration**: Single-click launch via `.bat` or `.sh` files. No database setup required.
- **Transparency**: Streak calculations include "Skip" days as transparent (they don't count for/against the streak), respecting the reality of human life.
- **Safe Self-Healing**: Built-in database integrity checks and repair tools ensure data longevity. We prioritize **Safe Self-Healing**, meaning corrupted databases are moved to a `.corrupt` extension rather than deleted.
- **Progressive Enhancement (PWA)**: The app works perfectly as a standard web page but upgrades to a native-like experience on supported devices, with offline capabilities and installability.

## 4. Data Transparency & Insight

We believe that data isn't just for storage; it's for **understanding**. The **Analytics Dashboard** transforms raw logs into visual insights. By showing trends (Activity) and reliability (Consistency), we empower users to see the "long game," turning data into actionable motivation without compromising privacy.

## 5. Target Audience & Use Cases

- **Privacy-Conscious Individuals**: People who want to track personal habits/notes without cloud exposure.
- **"Late Owls"**: Users who stay up past midnight and need the app to reflect their actual "awake day" via Day Extension logic.
- **Data Nerds**: Users who want full access to their data via CSV exports while enjoying a beautiful UI.

## 5. Real-world Workflow Fit

The tracker is designed to be pinned as a tab or run locally during a morning/evening routine. It supports keyboard shortcuts (`Ctrl+N` for new habits) to minimize friction in habit entry.

## 6. Trade-offs & Constraints

- **Single User**: Designed for one person per installation.
- **No Native Notifications**: Being browser-based/local, it doesn't send push notifications.
- **Browser-Dependence**: Requires a modern browser to render correctly.
```
