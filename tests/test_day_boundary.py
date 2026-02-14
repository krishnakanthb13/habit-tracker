
import unittest
from datetime import datetime
from app.services.day_boundary import get_effective_date, get_effective_today

class DayBoundaryTestCase(unittest.TestCase):
    
    # --- Happy Path Tests ---

    def test_mid_day_no_extension(self):
        """12 PM with extension off -> same day."""
        ts = datetime(2026, 2, 14, 12, 0, 0)
        res = get_effective_date(ts, day_extension=False)
        self.assertEqual(res, "2026-02-14")

    def test_late_night_extension_on(self):
        """2 AM with extension ON (cutoff 3) -> yesterday."""
        ts = datetime(2026, 2, 14, 2, 0, 0)
        res = get_effective_date(ts, day_extension=True, cutoff_hour=3)
        self.assertEqual(res, "2026-02-13")

    def test_late_night_extension_off(self):
        """2 AM with extension OFF (cutoff 3) -> today (calendar date)."""
        ts = datetime(2026, 2, 14, 2, 0, 0)
        res = get_effective_date(ts, day_extension=False, cutoff_hour=3)
        self.assertEqual(res, "2026-02-14")

    def test_past_cutoff_extension_on(self):
        """4 AM with extension ON (cutoff 3) -> today."""
        ts = datetime(2026, 2, 14, 4, 0, 0)
        res = get_effective_date(ts, day_extension=True, cutoff_hour=3)
        self.assertEqual(res, "2026-02-14")

    # --- Edge Case Tests ---

    def test_exactly_at_cutoff(self):
        """Exactly 3:00 AM with cutoff 3 -> today."""
        ts = datetime(2026, 2, 14, 3, 0, 0)
        res = get_effective_date(ts, day_extension=True, cutoff_hour=3)
        self.assertEqual(res, "2026-02-14")

    def test_cutoff_midnight(self):
        """Cutoff 0 (midnight) -> essentially extension OFF behavior."""
        ts = datetime(2026, 2, 14, 0, 30, 0)
        res = get_effective_date(ts, day_extension=True, cutoff_hour=0)
        self.assertEqual(res, "2026-02-14")

    # --- Settings Integration ---

    def test_get_effective_today_integration(self):
        """Test the helper that reads from settings dict."""
        settings = {
            "day_extension": "true",
            "day_extension_hour": "4"
        }
        # We can't easily mock datetime.now() without a library like freezegun
        # but we can verify the logic correctly parses the settings and calls the core function.
        # Here we just verify that get_effective_today doesn't crash and returns a date string.
        res = get_effective_today(settings)
        self.assertEqual(len(res), 10) # YYYY-MM-DD
        self.assertTrue(res.startswith("20"))

if __name__ == '__main__':
    unittest.main()
