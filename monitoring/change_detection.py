"""Deterministic snapshot hashing and field-level change detection."""
from __future__ import annotations
import hashlib
import json
from typing import Any

ALLOWED_FIELDS = {
    "record_status", "survey_number", "subdivision_number", "extent",
    "recorded_owner_name", "mutation_status", "record_date", "parcel_id",
}


def normalize_snapshot(record: dict[str, Any]) -> dict[str, Any]:
    """Keep a minimal allow-list of normalized fields; do not ingest arbitrary PII."""
    normalized = {}
    for key in sorted(ALLOWED_FIELDS):
        value = record.get(key)
        if value is not None:
            normalized[key] = " ".join(str(value).strip().split())
    return normalized


def snapshot_hash(record: dict[str, Any]) -> str:
    payload = json.dumps(normalize_snapshot(record), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def compare_snapshots(before: dict[str, Any], after: dict[str, Any]) -> list[dict[str, Any]]:
    """Return observed differences only. Caller must establish source and authorization."""
    old, new = normalize_snapshot(before), normalize_snapshot(after)
    return [
        {"field": field, "previous": old.get(field), "current": new.get(field)}
        for field in sorted(set(old) | set(new))
        if old.get(field) != new.get(field)
    ]


def classify_check(*, source_retrieved: bool, before: dict[str, Any] | None,
                   after: dict[str, Any] | None) -> dict[str, Any]:
    """A failed retrieval must never be presented as 'no change'."""
    if not source_retrieved or after is None:
        return {"status": "source_unavailable", "changes": [], "customer_alert_allowed": False}
    if before is None:
        return {"status": "baseline_created", "changes": [], "customer_alert_allowed": False}
    changes = compare_snapshots(before, after)
    return {
        "status": "source_changed" if changes else "no_change_observed",
        "changes": changes,
        "customer_alert_allowed": bool(changes),
    }
