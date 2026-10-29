import json
import tempfile
import unittest
from pathlib import Path

import db
from monitoring.store import (
    get_check_history, get_preferences, init_monitoring_store, log_check,
    save_owner_snapshot, save_preferences,
)


class MonitoringStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        db.DB_PATH = Path(self.temp.name) / "test.db"
        with db.conn() as c:
            c.execute("CREATE TABLE properties (id INTEGER PRIMARY KEY, property_code TEXT)")
            c.execute("INSERT INTO properties(id, property_code) VALUES(1, 'TEST-1')")
        init_monitoring_store()

    def tearDown(self):
        self.temp.cleanup()

    def test_preferences_round_trip(self):
        save_preferences(1, physical_enabled=True, government_enabled=False,
                         alert_email=True, alert_sms=False, alert_whatsapp=True)
        result = get_preferences(1)
        self.assertEqual(result["physical_enabled"], 1)
        self.assertEqual(result["government_enabled"], 0)
        self.assertEqual(result["alert_whatsapp"], 1)

    def test_first_snapshot_creates_baseline_then_detects_change(self):
        first = save_owner_snapshot(1, {"survey_number": " 124/2 ", "extent": "500 sq yards"})
        self.assertEqual(first["status"], "baseline_created")
        second = save_owner_snapshot(1, {"survey_number": "124/2", "extent": "600 sq yards"})
        self.assertEqual(second["status"], "source_changed")
        self.assertEqual(second["changes"][0]["field"], "extent")

    def test_unapproved_fields_are_not_saved(self):
        with self.assertRaises(ValueError):
            save_owner_snapshot(1, {"phone_number": "0000000000", "address": "private"})

    def test_unavailable_source_is_logged_as_unavailable(self):
        log_check(1, "government_records", "source_unavailable", "Access is not configured.")
        history = get_check_history(1)
        self.assertEqual(history[0]["status"], "source_unavailable")
        self.assertEqual(history[0]["source_type"], "government_records")


if __name__ == "__main__":
    unittest.main()
