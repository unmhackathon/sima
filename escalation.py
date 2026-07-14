from config import ESCALATION_EMAIL, TEAMS_WEBHOOK_URL


def send_teams_webhook(message: str) -> None:
    print("[Teams webhook message]")
    print(message)


def send_email(subject: str, body: str) -> None:
    print("[Email message]")
    print(subject)
    print(body)


def notify_lead(tickets: list[dict]) -> None:
    if not tickets:
        return

    lines = [
        "ServiceNow escalation: critical tickets requiring immediate lead attention",
        "",
    ]
    for ticket in tickets:
        notes = []
        if ticket.get("reasons"):
            notes.append(f"Reasons: {', '.join(ticket['reasons'])}")
        reason_text = f" | {'; '.join(notes)}" if notes else ""
        lines.append(
            f"{ticket['number']} | Priority {ticket.get('priority')} | Score {ticket['score']} | {ticket['summary']}{reason_text}"
        )
    body = "\n".join(lines)

    if TEAMS_WEBHOOK_URL:
        send_teams_webhook(body)
    else:
        print("No Teams webhook configured, printing escalation summary instead.")

    if ESCALATION_EMAIL:
        send_email("ServiceNow Critical Ticket Escalation", body)
    else:
        print("No escalation email configured, printing summary instead.")
