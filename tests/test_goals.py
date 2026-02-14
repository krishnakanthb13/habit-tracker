
import unittest
import os
import sys
from datetime import datetime, timedelta
import tempfile

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.database import get_db, init_db
from app.services.goals import evaluate_goal

class GoalsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.app.config['DATABASE_PATH'] = self.db_path
        
        with self.app.app_context():
            init_db(self.app)
            self.db = get_db()
            # Create a test habit
            self.db.execute("INSERT INTO habits (id, name) VALUES (1, 'Goal Habit')")
            self.db.commit()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def _add_entry(self, date_str, status='done'):
        with self.app.app_context():
            db = get_db()
            db.execute(
                "INSERT INTO entries (habit_id, entry_date, status) VALUES (?, ?, ?)",
                (1, date_str, status)
            )
            db.commit()

    def _set_goal(self, goal_type, target, period_days=7):
        with self.app.app_context():
            db = get_db()
            db.execute(
                "INSERT INTO goals (habit_id, goal_type, target, period_days) VALUES (?, ?, ?, ?)",
                (1, goal_type, target, period_days)
            )
            db.commit()

    # --- Happy Path Tests ---

    def test_daily_goal_met(self):
        """Standard daily goal: done today -> met."""
        today_str = datetime.now().strftime('%Y-%m-%d')
        self._set_goal('daily', 1)
        self._add_entry(today_str, 'done')
        
        with self.app.app_context():
            res = evaluate_goal(get_db(), 1, today_str)
            self.assertTrue(res['met'])
            self.assertEqual(res['current'], 1)

    def test_weekly_goal_met(self):
        """Weekly goal: 3 times a week, 3 done -> met."""
        # Use a fixed date to avoid weekend/monday issues if run on specific days
        # 2026-02-14 is Saturday. Week starts 2026-02-09 (Monday).
        fixed_today = "2026-02-14" 
        self._set_goal('weekly', 3)
        self._add_entry("2026-02-09", 'done')
        self._add_entry("2026-02-11", 'done')
        self._add_entry("2026-02-14", 'done')
        
        with self.app.app_context():
            res = evaluate_goal(get_db(), 1, fixed_today)
            self.assertTrue(res['met'])
            self.assertEqual(res['current'], 3)

    def test_custom_goal_met(self):
        """Custom goal: 2 times in 5 days, 2 done -> met."""
        fixed_today = "2026-02-14"
        self._set_goal('custom', 2, period_days=5)
        self._add_entry("2026-02-10", 'done') # 4 days ago
        self._add_entry("2026-02-14", 'done') # today
        
        with self.app.app_context():
            res = evaluate_goal(get_db(), 1, fixed_today)
            self.assertTrue(res['met'])
            self.assertEqual(res['current'], 2)

    # --- Edge Case Tests ---

    def test_no_goal_set(self):
        """If no goal is set, evaluate_goal should return None."""
        with self.app.app_context():
            # habit 1 has no goal row
            res = evaluate_goal(get_db(), 1)
            self.assertIsNone(res)

    def test_weekly_goal_monday(self):
        """On a Monday, only Monday's entries should count for the week."""
        monday = "2026-02-09"
        self._set_goal('weekly', 2)
        self._add_entry("2026-02-08", 'done') # Sunday (prev week)
        self._add_entry("2026-02-09", 'done') # Monday (this week)
        
        with self.app.app_context():
            res = evaluate_goal(get_db(), 1, monday)
            self.assertEqual(res['current'], 1)
            self.assertFalse(res['met'])

    def test_goal_not_met_partial(self):
        """Goal set to 5, only 3 done -> met: False."""
        fixed_today = "2026-02-14"
        self._set_goal('weekly', 5)
        self._add_entry("2026-02-10", 'done')
        self._add_entry("2026-02-11", 'done')
        self._add_entry("2026-02-12", 'done')
        
        with self.app.app_context():
            res = evaluate_goal(get_db(), 1, fixed_today)
            self.assertFalse(res['met'])
            self.assertEqual(res['current'], 3)

    # --- Error Handling ---

    def test_invalid_habit_id(self):
        """Evaluation for non-existent habit id should return None (matches no-goal-set behavior)."""
        with self.app.app_context():
            res = evaluate_goal(get_db(), 999)
            self.assertIsNone(res)

if __name__ == '__main__':
    unittest.main()
