import sqlite3
from pathlib import Path
import config


def query_incident_audit_log(db_path: str, limit: int = 20):
    if not Path(db_path).exists():
        print(f"Database file not found: {db_path}")
        return

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT * FROM incident_audit_log ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows = cursor.fetchall()
        if not rows:
            print("No audit records found.")
            return

        columns = rows[0].keys()
        widths = [max(len(col), max(len(str(row[col])) for row in rows)) for col in columns]
        header = " | ".join(col.ljust(width) for col, width in zip(columns, widths))
        separator = "-+-".join('-' * width for width in widths)

        print(header)
        print(separator)
        for row in rows:
            print(" | ".join(str(row[col]).ljust(width) for col, width in zip(columns, widths)))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Query the ServiceNow Sima incident audit SQLite database.")
    parser.add_argument(
        "--db",
        default=config.SQLITE_AUDIT_DB,
        help="Path to the SQLite audit database file.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Number of records to show.",
    )
    args = parser.parse_args()
    query_incident_audit_log(args.db, args.limit)
