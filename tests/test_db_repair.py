
import unittest
import os
import sys
import tempfile
import sqlite3
from app.services.db_repair import integrity_check, create_backup

class DBRepairTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        # Create a valid DB
        conn = sqlite3.connect(self.db_path)
        conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
        conn.commit()
        conn.close()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    # --- Happy Path Tests ---

    def test_integrity_check_healthy(self):
        """Standard check on a healthy database."""
        res = integrity_check(self.db_path)
        self.assertTrue(res['ok'])
        self.assertEqual(res['details'], ["ok"])

    def test_create_backup_success(self):
        """Verify backup file is created in the backup directory."""
        backup_dir = os.path.join(self.temp_dir, "backups")
        backup_path = create_backup(self.db_path, backup_dir)
        
        self.assertTrue(os.path.exists(backup_path))
        self.assertTrue(backup_path.startswith(backup_dir))
        # Verify it's a copy
        self.assertEqual(os.path.getsize(self.db_path), os.path.getsize(backup_path))

    # --- Edge Cases ---

    def test_integrity_check_not_a_db(self):
        """Check integrity on a non-database file."""
        not_db_path = os.path.join(self.temp_dir, "not.db")
        with open(not_db_path, "w") as f:
            f.write("This is not a sqlite database.")
        
        res = integrity_check(not_db_path)
        self.assertFalse(res['ok'])
        # SQLite might return "file is not a database" or similar in details
        self.assertNotEqual(res['details'], ["ok"])

    # --- Error Handling ---

    def test_create_backup_invalid_dir(self):
        """Try to backup to a path that isn't a directory (or is protected)."""
        # Create a file where a directory should be
        protected_dir = os.path.join(self.temp_dir, "blocked")
        with open(protected_dir, "w") as f:
            f.write("I am a file")
        
        with self.assertRaises(Exception):
            create_backup(self.db_path, protected_dir)

if __name__ == '__main__':
    unittest.main()
