import sqlite3
from datetime import datetime, timezone
from typing import Iterable


def _ensure_audit_table(db_path: str) -> None:
    with sqlite3.connect(db_path, timeout=30) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS incident_audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_number TEXT,
                priority TEXT,
                state TEXT,
                severity TEXT,
                score INTEGER,
                stale INTEGER,
                invalid_activity_logs INTEGER,
                missing_update_data INTEGER,
                summary TEXT,
                short_description TEXT,
                description TEXT,
                comments TEXT,
                activity_logs TEXT,
                sys_updated_on TEXT,
                sys_created_on TEXT,
                reason TEXT,
                created_at TEXT
            )
            """
        )
        conn.commit()


def _bool_to_int(value: bool) -> int:
    return 1 if value else 0


def append_needs_update_records(db_path: str, tickets: list[dict]) -> None:
    if not tickets:
        return

    _ensure_audit_table(db_path)
    now = datetime.now(timezone.utc).isoformat()

    records = []
    for ticket in tickets:
        records.append(
            (
                ticket.get("number"),
                ticket.get("priority"),
                ticket.get("state"),
                ticket.get("severity"),
                ticket.get("score"),
                _bool_to_int(ticket.get("stale", False)),
                _bool_to_int(ticket.get("invalid_activity_logs", False)),
                _bool_to_int(ticket.get("missing_update_data", False)),
                ticket.get("summary"),
                ticket.get("short_description"),
                ticket.get("description"),
                ticket.get("comments"),
                ticket.get("activity_logs"),
                ticket.get("sys_updated_on"),
                ticket.get("sys_created_on"),
                ticket.get("reason"),
                now,
            )
        )

    with sqlite3.connect(db_path, timeout=30) as conn:
        conn.executemany(
            """
            INSERT INTO incident_audit_log (
                ticket_number,
                priority,
                state,
                severity,
                score,
                stale,
                invalid_activity_logs,
                missing_update_data,
                summary,
                short_description,
                description,
                comments,
                activity_logs,
                sys_updated_on,
                sys_created_on,
                reason,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            records,
        )
        conn.commit()
