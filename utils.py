
def render_ticket(ticket: dict) -> str:
    return (
        f"{ticket.get('number')} | {ticket.get('short_description')} "
        f"(Priority {ticket.get('priority')}, State {ticket.get('state')})"
    )


def ticket_full_text(ticket: dict) -> str:
    parts = [
        ticket.get("short_description", ""),
        ticket.get("description", ""),
        ticket.get("comments", ""),
    ]
    return "\n".join(part for part in parts if part)
