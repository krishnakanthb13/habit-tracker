
import unittest
import json
import os
import sys
import tempfile
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.config import Config

class TestConfig(Config):
    TESTING = True
    # DATABASE_PATH set in setUp

class SmokeTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        
        class LocalTestConfig(TestConfig):
             DATABASE_PATH = self.db_path
             DATABASE_DIR = os.path.dirname(self.db_path)
        
        self.app = create_app(LocalTestConfig)
        self.client = self.app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_health_check(self):
        """Test the health check endpoint."""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['ok'])

    def test_habits_crud(self):
        """Test creating and listing habits."""
        # Create
        habit_data = {'name': 'Smoke Habit', 'description': 'Testing', 'color': '#ff0000'}
        response = self.client.post('/api/habits', json=habit_data)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Smoke Habit')
        habit_id = data['id']

        # List
        response = self.client.get('/api/habits')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(len(data) >= 1)
        # Verify the created habit is in the list
        found = any(h['id'] == habit_id for h in data)
        self.assertTrue(found)

    def test_calendar(self):
        """Test calendar data retrieval."""
        today = datetime.now().strftime('%Y-%m')
        response = self.client.get(f'/api/calendar?month={today}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('habits', data)
        self.assertIn('days_in_month', data)

    def test_settings(self):
        """Test settings endpoint."""
        response = self.client.get('/api/settings')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        # Should have default settings
        self.assertIn('theme', data)
        self.assertIn('day_extension', data)

if __name__ == '__main__':
    unittest.main()
