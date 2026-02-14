
import unittest
import io
import os
import sys
import tempfile
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.database import get_db, init_db
from app.services.csv_handler import (
    _identify_table, _rows_to_csv, _validate_entry, import_csv
)

class CSVHandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.app.config['DATABASE_PATH'] = self.db_path
        
        with self.app.app_context():
            init_db(self.app)
            self.db = get_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    # --- Happy Path Tests ---

    def test_identify_table(self):
        """Test header identification logic."""
        h_habits = ["id", "name", "description", "color", "position"]
        h_entries = ["habit_id", "entry_date", "status", "note"]
        h_goals = ["habit_id", "goal_type", "target"]
        h_settings = ["key", "value"]

        self.assertEqual(_identify_table(h_habits)[0], "habits")
        self.assertEqual(_identify_table(h_entries)[0], "entries")
        self.assertEqual(_identify_table(h_goals)[0], "goals")
        self.assertEqual(_identify_table(h_settings)[0], "settings")

    def test_rows_to_csv(self):
        """Standard row-to-csv string conversion."""
        rows = [{"a": 1, "b": "foo"}, {"a": 2, "b": "bar"}]
        headers = ["a", "b"]
        res = _rows_to_csv(rows, headers)
        expected = "a,b\r\n1,foo\r\n2,bar\r\n"
        self.assertEqual(res, expected)

    def test_import_csv_habits(self):
        """Import habits from CSV string."""
        csv_content = "name,description,color\nRunning,Daily run,#FF0000\nReading,Books,#00FF00"
        with self.app.app_context():
            res = import_csv(get_db(), csv_content, "habits")
            self.assertEqual(res['imported'], 2)
            self.assertEqual(len(res['errors']), 0)
            
            # Verify in DB
            habits = get_db().execute("SELECT name FROM habits").fetchall()
            names = [h['name'] for h in habits]
            self.assertIn("Running", names)
            self.assertIn("Reading", names)

    # --- Edge Cases ---

    def test_identify_table_unknown(self):
        """Wait, what if headers are random?"""
        h_random = ["foo", "bar", "baz"]
        table, errors = _identify_table(h_random)
        self.assertIsNone(table)
        self.assertTrue(len(errors) > 0)

    def test_import_empty_csv(self):
        """Importing empty CSV should result in 0 imports, no errors."""
        csv_content = "name,description,color\n"
        with self.app.app_context():
            res = import_csv(get_db(), csv_content, "habits")
            self.assertEqual(res['imported'], 0)
            self.assertEqual(len(res['errors']), 0)

    # --- Error Handling ---

    def test_validate_entry_errors(self):
        """Test validation rules for entry rows."""
        # Missing habit_id
        with self.assertRaisesRegex(ValueError, "Missing habit_id"):
            _validate_entry({"entry_date": "2026-02-14", "status": "done"})
        
        # Invalid status
        with self.assertRaisesRegex(ValueError, "Invalid status"):
            _validate_entry({"habit_id": 1, "entry_date": "2026-02-14", "status": "maybe"})
        
        # Malformed date
        with self.assertRaisesRegex(ValueError, "Invalid date format"):
            _validate_entry({"habit_id": 1, "entry_date": "14-02-2026", "status": "done"})

    def test_import_csv_errors(self):
        """Import CSV with some faulty rows."""
        # Test entries validation instead of habits (habits has loose validation currently)
        csv_content = "habit_id,entry_date,status\n1,2026-02-14,done\n1,2026-02-15,invalid"
        with self.app.app_context():
            res = import_csv(get_db(), csv_content, "entries")
            # Row 1 imports (if habit 1 exists, but wait, keys check...), Row 2 fails
            # Actually entries needs habit_id to exist if foreign keys are on.
            # But INSERT OR REPLACE might fail on FK if habit doesn't exist.
            self.assertEqual(res['imported'], 0) # Both fail because habit 1 doesn't exist (FK)
            self.assertEqual(len(res['errors']), 2)

if __name__ == '__main__':
    unittest.main()
