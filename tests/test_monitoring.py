import unittest
from monitoring.change_detection import normalize_snapshot, snapshot_hash, compare_snapshots, classify_check
from monitoring.providers import provider_status


class ChangeDetectionTests(unittest.TestCase):
    def test_hash_is_stable(self):
        self.assertEqual(snapshot_hash({"extent": " 2 acres ", "record_status": "Active"}),
                         snapshot_hash({"record_status": "Active", "extent": "2 acres"}))

    def test_unapproved_fields_are_ignored(self):
        self.assertEqual(normalize_snapshot({"extent": "2 acres", "aadhaar": "1234"}), {"extent": "2 acres"})

    def test_detects_field_change(self):
        self.assertEqual(compare_snapshots({"extent": "1 acre"}, {"extent": "2 acres"}),
                         [{"field": "extent", "previous": "1 acre", "current": "2 acres"}])

    def test_source_failure_is_not_no_change(self):
        self.assertEqual(classify_check(source_retrieved=False, before={"extent": "1"}, after=None),
                         {"status": "source_unavailable", "changes": [], "customer_alert_allowed": False})

    def test_first_record_is_baseline_not_alert(self):
        self.assertEqual(classify_check(source_retrieved=True, before=None, after={"extent": "1"}),
                         {"status": "baseline_created", "changes": [], "customer_alert_allowed": False})

    def test_government_sources_are_explicitly_blocked(self):
        self.assertTrue(all(p["live_monitoring"] is False for p in provider_status()))
        self.assertTrue(all(p["status"] == "blocked_government_access" for p in provider_status()))


if __name__ == "__main__":
    unittest.main()
