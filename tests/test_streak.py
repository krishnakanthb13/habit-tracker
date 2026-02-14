
import unittest
import os
import sys
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.database import get_db, init_db
from app.services.streak import calculate_streaks

class StreakTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        # Use a temporary file for DB to avoid in-memory issues with certain SQLite features
        # although :memory: usually works for these tests, we'll stick to a temp file for consistency
        import tempfile
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.app.config['DATABASE_PATH'] = self.db_path
        
        with self.app.app_context():
            init_db(self.app)
            self.db = get_db()
            # Create a test habit
            self.db.execute(
                "INSERT INTO habits (id, name, created_at) VALUES (1, 'Test Habit', ?)",
                ((datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S'),)
            )
            self.db.commit()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def _add_entry(self, date_str, status):
        with self.app.app_context():
            db = get_db()
            db.execute(
                "INSERT INTO entries (habit_id, entry_date, status) VALUES (?, ?, ?)",
                (1, date_str, status)
            )
            db.commit()

    def test_basic_streak(self):
        """Test a simple consecutive streak."""
        today = datetime.now()
        self._add_entry(today.strftime('%Y-%m-%d'), 'done')
        self._add_entry((today - timedelta(days=1)).strftime('%Y-%m-%d'), 'done')
        self._add_entry((today - timedelta(days=2)).strftime('%Y-%m-%d'), 'done')

        with self.app.app_context():
            res = calculate_streaks(get_db(), 1, skip_enabled=True, effective_today=today.strftime('%Y-%m-%d'))
            self.assertEqual(res['current_streak'], 3)
            self.assertEqual(res['best_streak'], 3)
            self.assertEqual(res['total_done'], 3)

    def test_broken_streak(self):
        """Test that a 'miss' breaks the streak."""
        today = datetime.now()
        self._add_entry(today.strftime('%Y-%m-%d'), 'done')
        # Day 1: Done, Day 2: Miss, Day 3: Done
        self._add_entry((today - timedelta(days=2)).strftime('%Y-%m-%d'), 'done')
        
        with self.app.app_context():
            res = calculate_streaks(get_db(), 1, skip_enabled=True, effective_today=today.strftime('%Y-%m-%d'))
            self.assertEqual(res['current_streak'], 1)
            self.assertEqual(res['best_streak'], 1)
            self.assertEqual(res['total_done'], 2)

    def test_skip_transparency(self):
        """Test that 'skip' is transparent (doesn't break or extend)."""
        today = datetime.now()
        self._add_entry(today.strftime('%Y-%m-%d'), 'done')
        self._add_entry((today - timedelta(days=1)).strftime('%Y-%m-%d'), 'skip')
        self._add_entry((today - timedelta(days=2)).strftime('%Y-%m-%d'), 'done')

        with self.app.app_context():
            # Skip enabled: streak should be 2
            res = calculate_streaks(get_db(), 1, skip_enabled=True, effective_today=today.strftime('%Y-%m-%d'))
            self.assertEqual(res['current_streak'], 2)
            
            # Skip disabled: skip is treated as miss, streak should be 1
            res = calculate_streaks(get_db(), 1, skip_enabled=False, effective_today=today.strftime('%Y-%m-%d'))
            self.assertEqual(res['current_streak'], 1)

    def test_future_entries(self):
        """Test that future entries don't affect current streak if scanning from today."""
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        self._add_entry(today.strftime('%Y-%m-%d'), 'done')
        self._add_entry(tomorrow.strftime('%Y-%m-%d'), 'done')

        with self.app.app_context():
            res = calculate_streaks(get_db(), 1, skip_enabled=True, effective_today=today.strftime('%Y-%m-%d'))
            self.assertEqual(res['current_streak'], 1)

    def test_habit_creation_floor(self):
        """Test that streak doesn't break if no entries exist before habit creation."""
        # Habit created 10 days ago. Entry today.
        today = datetime.now()
        self._add_entry(today.strftime('%Y-%m-%d'), 'done')
        
        with self.app.app_context():
            res = calculate_streaks(get_db(), 1, skip_enabled=True, effective_today=today.strftime('%Y-%m-%d'))
            # It only goes back to yesterday, sees nothing, but since it's within floor it might break?
            # Actually, streak logic breaks on NULL (no entry) if it's past.
            # So today = 1, yesterday = NULL -> current_streak = 1.
            self.assertEqual(res['current_streak'], 1)

if __name__ == '__main__':
    unittest.main()
