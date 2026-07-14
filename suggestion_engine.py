from config import STALE_THRESHOLD_HOURS


def build_ticket_summary(ticket: dict, evaluation: dict) -> str:
    return (
        f"{ticket.get('number')} - {ticket.get('short_description')} "
        f"(Priority {ticket.get('priority')} | Severity: {evaluation['severity']})"
    )


def suggestion_text(ticket: dict, evaluation: dict) -> str:
    nlp = evaluation["nlp"]
    stale_note = (
        f"The ticket has not been updated in the last {STALE_THRESHOLD_HOURS} hours."
        if evaluation["stale"]
        else "Recent activity is present."
    )
    intent_phrase = {
        "blocked": "The issue appears to be blocking the user from continuing work.",
        "failed": "The user reports a failure or repeat error condition.",
        "not_working": "The service or function is not working as expected.",
        "informational": "The user has described a concern that should be clarified.",
    }.get(nlp["intent"], "Review the user concern and update the ticket details.")

    action_items = [
        f"Confirm the current status of the user concern: {nlp['concern']}",
        "Add the latest actions taken or troubleshooting steps performed.",
        "Set the expected next update time and the owner responsible for follow-up.",
    ]

    if evaluation.get("invalid_activity_logs"):
        action_items.append(
            "Review the activity log content and replace invalid or placeholder entries with actual progress details."
        )

    if evaluation.get("missing_update_data"):
        action_items.append(
            "Capture the latest update or comment on ticket progress because the ticket is missing fresh update data."
        )

    if nlp["urgency"] == "high":
        action_items.insert(0, "Mark this ticket as high urgency and notify the appropriate resolver team.")

    if nlp["sentiment"] == "negative":
        action_items.append("Acknowledge the user impact and share next steps clearly.")

    return (
        f"Suggested update for {ticket.get('number')}:\n"
        f"- {stale_note}\n"
        f"- {intent_phrase}\n"
        f"- Customer concern: {nlp['concern']}\n"
        f"- Urgency: {nlp['urgency']}\n"
        f"- Sentiment: {nlp['sentiment']}\n"
        "- Recommended actions:\n"
        + "\n".join(f"  * {item}" for item in action_items)
    )


def criticality_label(score: int) -> str:
    if score >= 6:
        return "Critical"
    if score >= 3:
        return "Needs Update"
    return "Monitor"
