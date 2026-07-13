import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TRACKER_FILE = Path("agent_state.json")
RESOLVED_STATES = {"closed", "resolved", "cancelled", "canceled"}


def _load_state() -> dict[str, Any]:
    if not TRACKER_FILE.exists():
        return {
            "tickets": {},
            "metrics": {"resolved_by_agent": 0, "last_run": None},
            "priority_history": [],
        }
    try:
        return json.load(TRACKER_FILE.open("r", encoding="utf-8"))
    except json.JSONDecodeError:
        return {
            "tickets": {},
            "metrics": {"resolved_by_agent": 0, "last_run": None},
            "priority_history": [],
        }


def _save_state(state: dict[str, Any]) -> None:
    TRACKER_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _normalize_state(value: str) -> str:
    return str(value or "").strip().lower()


def update_ticket_history(ticket: dict, evaluation: dict, state: dict[str, Any]) -> None:
    number = ticket.get("number") or ticket.get("sys_id")
    if not number:
        return

    current_state = _normalize_state(ticket.get("state", ""))
    flagged = evaluation["severity"] in {"critical", "needs_update"}
    ticket_record = state["tickets"].get(number, {
        "number": number,
        "last_state": "",
        "last_severity": "",
        "flagged": False,
        "resolved_by_agent": False,
        "last_seen_on": None,
    })

    if ticket_record["flagged"] and not ticket_record["resolved_by_agent"]:
        if current_state in RESOLVED_STATES and ticket_record["last_state"] not in RESOLVED_STATES:
            state["metrics"]["resolved_by_agent"] = state["metrics"].get("resolved_by_agent", 0) + 1
            ticket_record["resolved_by_agent"] = True

    ticket_record.update({
        "last_state": current_state,
        "last_severity": evaluation["severity"],
        "flagged": flagged,
        "last_seen_on": datetime.now(timezone.utc).isoformat(),
    })
    state["tickets"][number] = ticket_record


def append_priority_snapshot(state: dict[str, Any], counts: dict[str, int], max_history: int = 20) -> None:
    history = state.setdefault("priority_history", [])
    snapshot = {"timestamp": datetime.now(timezone.utc).isoformat()}
    snapshot.update({str(i): counts.get(str(i), 0) for i in range(1, 6)})
    history.append(snapshot)
    state["priority_history"] = history[-max_history:]


def get_priority_history(state: dict[str, Any]) -> list[dict[str, Any]]:
    return state.get("priority_history", [])


def load_state() -> dict[str, Any]:
    return _load_state()


def save_state(state: dict[str, Any]) -> None:
    if state.get("metrics") is None:
        state["metrics"] = {"resolved_by_agent": 0, "last_run": None}
    state["metrics"]["last_run"] = datetime.now(timezone.utc).isoformat()
    _save_state(state)


def get_metrics(state: dict[str, Any]) -> dict[str, Any]:
    result = {
        "resolved_by_agent": state.get("metrics", {}).get("resolved_by_agent", 0),
        "last_run": state.get("metrics", {}).get("last_run"),
        "tracked_tickets": len(state.get("tickets", {})),
    }
    return result


def get_flagged_tickets(state: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        ticket_data
        for ticket_data in state.get("tickets", {}).values()
        if ticket_data.get("flagged")
    ]
