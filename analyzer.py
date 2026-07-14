import re
from datetime import date, datetime, timezone
from config import STALE_THRESHOLD_HOURS, CRITICAL_THRESHOLD, UPDATE_THRESHOLD
from nlp_processor import analyze_ticket_text, normalize_text

SERVICE_NOW_DATE_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%S.%f",
]

INVALID_ACTIVITY_PLACEHOLDERS = {
    "none",
    "n/a",
    "na",
    "unknown",
    "pending",
    "no activity",
    "not available",
    "not applicable",
    "test",
    "testing",
    "placeholder",
    "tbd",
    "todo",
    "tet",
    "tesst",
    "tet tesst",
}


def parse_servicenow_date(value: str | date | datetime | None) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)

    normalized_value = str(value).strip()
    if not normalized_value:
        return None
    for fmt in SERVICE_NOW_DATE_FORMATS:
        try:
            return datetime.strptime(normalized_value, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def hours_since_last_update(ticket: dict) -> float | None:
    updated_on = ticket.get("sys_updated_on") or ticket.get("sys_created_on")
    timestamp = parse_servicenow_date(updated_on)
    if not timestamp:
        return None
    return (datetime.now(timezone.utc) - timestamp).total_seconds() / 3600


def is_stale(ticket: dict) -> bool:
    hours = hours_since_last_update(ticket)
    return hours is not None and hours >= STALE_THRESHOLD_HOURS


def compute_criticality(ticket: dict, nlp: dict) -> int:
    score = 0
    priority = str(ticket.get("priority", "")).strip()
    if priority in {"1", "2"}:
        score += 3
    elif priority == "3":
        score += 1

    if is_stale(ticket):
        score += 2

    if nlp["sentiment"] == "negative":
        score += 2
    if nlp["urgency"] == "high":
        score += 2
    if nlp["intent"] in {"blocked", "failed", "not_working"}:
        score += 3

    return score


def is_placeholder_text(text: str) -> bool:
    normalized = normalize_text(text)
    if not normalized:
        return True
    if normalized in INVALID_ACTIVITY_PLACEHOLDERS:
        return True
    if normalized in {"...", "-", "--", "...", "??", "tet tesst"}:
        return True
    if len(normalized) <= 3 and not re.search(r"[a-z0-9]", normalized):
        return True
    if re.fullmatch(r"[.\-?\s]+", normalized):
        return True
    return False


def has_invalid_activity_logs(ticket: dict) -> bool:
    activity_logs = str(ticket.get("activity_logs", "")).strip()
    return is_placeholder_text(activity_logs)


def has_missing_update_data(ticket: dict) -> bool:
    if not parse_servicenow_date(ticket.get("sys_updated_on")):
        return True

    comments = str(ticket.get("comments", "")).strip()
    activity_logs = str(ticket.get("activity_logs", "")).strip()
    return is_placeholder_text(comments) and is_placeholder_text(activity_logs)


def evaluation(ticket: dict) -> dict:
    nlp = analyze_ticket_text(
        ticket.get("short_description", ""),
        ticket.get("description", ""),
        ticket.get("comments", ""),
        ticket.get("activity_logs", ""),
    )
    stale = is_stale(ticket)
    score = compute_criticality(ticket, nlp)
    invalid_activity_logs = has_invalid_activity_logs(ticket)
    missing_update_data = has_missing_update_data(ticket)

    if score >= CRITICAL_THRESHOLD:
        severity = "critical"
    elif score >= UPDATE_THRESHOLD or stale or invalid_activity_logs or missing_update_data:
        severity = "needs_update"
    else:
        severity = "monitor"

    return {
        "nlp": nlp,
        "stale": stale,
        "score": score,
        "severity": severity,
        "invalid_activity_logs": invalid_activity_logs,
        "missing_update_data": missing_update_data,
    }
