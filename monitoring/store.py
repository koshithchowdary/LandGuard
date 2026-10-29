"""SQLite persistence for monitoring preferences, snapshots and audit history.

This module records user-provided snapshots and connector check outcomes. It does not
fetch government portals or satellite imagery by itself.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from db import conn
from monitoring.change_detection import normalize_snapshot, snapshot_hash, classify_check

SCHEMA = """
CREATE TABLE IF NOT EXISTS monitoring_preferences (
    property_id INTEGER PRIMARY KEY,
    physical_enabled INTEGER NOT NULL DEFAULT 0,
    government_enabled INTEGER NOT NULL DEFAULT 0,
    alert_email INTEGER NOT NULL DEFAULT 0,
    alert_sms INTEGER NOT NULL DEFAULT 0,
    alert_whatsapp INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(property_id) REFERENCES properties(id)
);
CREATE TABLE IF NOT EXISTS monitoring_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL,
    source_type TEXT NOT NULL,
    snapshot_json TEXT NOT NULL,
    snapshot_hash TEXT NOT NULL,
    captured_at TEXT NOT NULL,
    FOREIGN KEY(property_id) REFERENCES properties(id)
);
CREATE TABLE IF NOT EXISTS monitoring_checks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL,
    source_type TEXT NOT NULL,
    status TEXT NOT NULL,
    summary TEXT NOT NULL,
    changes_json TEXT NOT NULL DEFAULT '[]',
    checked_at TEXT NOT NULL,
    FOREIGN KEY(property_id) REFERENCES properties(id)
);
"""


def init_monitoring_store() -> None:
    with conn() as c:
        c.executescript(SCHEMA)


def save_preferences(property_id: int, *, physical_enabled: bool, government_enabled: bool,
                     alert_email: bool, alert_sms: bool, alert_whatsapp: bool) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with conn() as c:
        c.execute(
            """INSERT INTO monitoring_preferences
               (property_id, physical_enabled, government_enabled, alert_email, alert_sms,
                alert_whatsapp, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(property_id) DO UPDATE SET
                 physical_enabled=excluded.physical_enabled,
                 government_enabled=excluded.government_enabled,
                 alert_email=excluded.alert_email, alert_sms=excluded.alert_sms,
                 alert_whatsapp=excluded.alert_whatsapp, updated_at=excluded.updated_at""",
            (property_id, int(physical_enabled), int(government_enabled), int(alert_email),
             int(alert_sms), int(alert_whatsapp), now),
        )


def get_preferences(property_id: int) -> dict[str, Any]:
    with conn() as c:
        row = c.execute(
            "SELECT * FROM monitoring_preferences WHERE property_id=?", (property_id,)
        ).fetchone()
    if not row:
        return {"physical_enabled": 0, "government_enabled": 0, "alert_email": 0,
                "alert_sms": 0, "alert_whatsapp": 0}
    return dict(row)


def log_check(property_id: int, source_type: str, status: str, summary: str,
              changes: list[dict[str, Any]] | None = None) -> None:
    with conn() as c:
        c.execute(
            """INSERT INTO monitoring_checks
               (property_id, source_type, status, summary, changes_json, checked_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (property_id, source_type, status, summary,
             json.dumps(changes or [], ensure_ascii=False),
             datetime.now(timezone.utc).isoformat()),
        )


def save_owner_snapshot(property_id: int, record: dict[str, Any]) -> dict[str, Any]:
    """Save a manually supplied record snapshot and compare it with the previous one."""
    normalized = normalize_snapshot(record)
    if not normalized:
        raise ValueError("No supported fields found. Add at least one allow-listed record field.")
    with conn() as c:
        previous = c.execute(
            """SELECT snapshot_json FROM monitoring_snapshots
               WHERE property_id=? AND source_type='owner_provided_document'
               ORDER BY id DESC LIMIT 1""", (property_id,)
        ).fetchone()
        before = json.loads(previous["snapshot_json"]) if previous else None
        result = classify_check(source_retrieved=True, before=before, after=normalized)
        c.execute(
            """INSERT INTO monitoring_snapshots
               (property_id, source_type, snapshot_json, snapshot_hash, captured_at)
               VALUES (?, 'owner_provided_document', ?, ?, ?)""",
            (property_id, json.dumps(normalized, ensure_ascii=False, sort_keys=True),
             snapshot_hash(normalized), datetime.now(timezone.utc).isoformat()),
        )
        status = result["status"]
        summary = {
            "baseline_created": "First owner-provided snapshot saved as baseline.",
            "source_changed": f"{len(result['changes'])} field change(s) observed between supplied snapshots.",
            "no_change_observed": "No differences observed between supplied snapshots.",
        }[status]
        c.execute(
            """INSERT INTO monitoring_checks
               (property_id, source_type, status, summary, changes_json, checked_at)
               VALUES (?, 'owner_provided_document', ?, ?, ?, ?)""",
            (property_id, status, summary, json.dumps(result["changes"], ensure_ascii=False),
             datetime.now(timezone.utc).isoformat()),
        )
    return result


def get_check_history(property_id: int, limit: int = 20) -> list[dict[str, Any]]:
    with conn() as c:
        rows = c.execute(
            """SELECT * FROM monitoring_checks WHERE property_id=?
               ORDER BY id DESC LIMIT ?""", (property_id, limit)
        ).fetchall()
    return [dict(row) for row in rows]
