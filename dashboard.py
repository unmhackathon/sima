import os
import sys
from pathlib import Path

import streamlit as st
from typing import Any

project_root = str(Path(__file__).resolve().parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

if "tracker" in sys.modules:
    imported_tracker = sys.modules["tracker"]
    if not getattr(imported_tracker, "__file__", "").startswith(project_root):
        del sys.modules["tracker"]

from analyzer import evaluation
from fetcher import fetch_active_incidents
from suggestion_engine import build_ticket_summary, suggestion_text
from tracker import (
    append_priority_snapshot,
    get_metrics,
    get_priority_history,
    load_state,
    save_state,
    update_ticket_history,
)


def process_dashboard_tickets() -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, int], list[dict[str, Any]]]:
    tickets = fetch_active_incidents()
    state = load_state()

    ticket_displays: list[dict[str, Any]] = []
    priority_counts = {str(i): 0 for i in range(1, 6)}

    for ticket in tickets:
        result = evaluation(ticket)
        summary = build_ticket_summary(ticket, result)
        update_ticket_history(ticket, result, state)
        number = ticket.get("number")
        priority = str(ticket.get("priority", "")).strip()
        if priority in priority_counts:
            priority_counts[priority] += 1

        ticket_displays.append({
            "number": number,
            "summary": summary,
            "state": ticket.get("state"),
            "priority": priority,
            "severity": result["severity"],
            "score": result["score"],
            "suggestion": suggestion_text(ticket, result),
            "last_updated": ticket.get("sys_updated_on"),
        })

    append_priority_snapshot(state, priority_counts)
    save_state(state)
    return ticket_displays, get_metrics(state), priority_counts, get_priority_history(state)


def run_dashboard() -> None:
    st.set_page_config(page_title="ServiceNow Agent Dashboard", layout="wide")
    st.title("ServiceNow Ticket Update Agent Dashboard")
    st.markdown(
        "This dashboard shows live ticket statistics and allows ticket lookup by severity and search text."
    )

    if st.sidebar.button("Refresh now"):
        try:
            st.rerun()
        except Exception:
            pass

    st.sidebar.markdown(
        "Update the Excel file, then click Refresh now to reload the dashboard with the latest ticket data."
    )

    tickets, metrics, priority_counts, priority_history = process_dashboard_tickets()

    status_counts = {"Fixed": 0, "In Progress": 0, "Closed": 0}
    for ticket in tickets:
        state = str(ticket.get("state", "")).strip().lower()
        if state in {"fixed", "resolved"}:
            status_counts["Fixed"] += 1
        elif state in {"closed", "cancelled", "canceled"}:
            status_counts["Closed"] += 1
        else:
            status_counts["In Progress"] += 1

    st.markdown("## Live ticket statistics")
    stat_cols = st.columns(3)
    stat_cols[0].metric("Tickets loaded", len(tickets))
    stat_cols[1].metric("Resolved via agent", metrics.get("resolved_by_agent", 0))
    stat_cols[2].metric("Last processed", metrics.get("last_run") or "Never")

    st.markdown("### Priority distribution")
    prio_cols = st.columns(5)
    for idx, priority in enumerate(["1", "2", "3", "4", "5"]):
        prio_cols[idx].metric(f"P{priority}", priority_counts[priority])

    st.markdown("### Priority trend")
    if priority_history:
        chart_data = {
            f"P{i}": [snapshot.get(str(i), 0) for snapshot in priority_history]
            for i in range(1, 6)
        }
        st.line_chart(chart_data)
        st.caption(
            f"Showing trend for the last {len(priority_history)} refreshes. Refresh after editing Excel to add new points."
        )
    else:
        st.info("Priority trend data appears after the first dashboard refresh.")

    st.markdown("### Status counts")
    status_cols = st.columns(3)
    status_cols[0].metric("Fixed", status_counts["Fixed"])
    status_cols[1].metric("In Progress", status_counts["In Progress"])
    status_cols[2].metric("Closed", status_counts["Closed"])

    st.markdown("## Ticket lookup")
    severity_filter = st.selectbox(
        "Filter by criticality",
        ["All", "critical", "needs_update", "monitor"],
        index=0,
    )
    search_text = st.text_input(
        "Search ticket number or text",
        value="",
        help="Enter ticket number, keyword, or phrase to filter the ticket list.",
    )

    if st.button("Show matching tickets"):
        filtered_tickets = []
        query = search_text.strip().lower()
        for ticket in tickets:
            if severity_filter != "All" and ticket["severity"] != severity_filter:
                continue
            if query:
                text = " ".join(
                    [
                        str(ticket.get("number", "")),
                        str(ticket.get("summary", "")),
                        str(ticket.get("state", "")),
                        str(ticket.get("priority", "")),
                    ]
                ).lower()
                if query not in text:
                    continue
            filtered_tickets.append(ticket)

        if filtered_tickets:
            st.markdown(f"### {len(filtered_tickets)} matching tickets")
            st.table(
                [
                    {
                        "Number": ticket["number"],
                        "Priority": ticket["priority"],
                        "Severity": ticket["severity"],
                        "State": ticket["state"],
                        "Last updated": ticket["last_updated"],
                    }
                    for ticket in filtered_tickets
                ]
            )
        else:
            st.info("No tickets matched the selected filters.")
    else:
        st.info("Use the filters above and click Show matching tickets to display incidents.")


if __name__ == "__main__":
    run_dashboard()
