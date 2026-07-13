import argparse
import logging
import time
from pathlib import Path

import config
from analyzer import evaluation
from escalation import notify_lead
from fetcher import fetch_active_incidents
from suggestion_engine import build_ticket_summary, suggestion_text

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


def process_tickets() -> None:
    tickets = fetch_active_incidents()
    logger.info("Processing %d tickets", len(tickets))

    escalations = []
    for ticket in tickets:
        result = evaluation(ticket)
        summary = build_ticket_summary(ticket, result)
        logger.info("Evaluated ticket: %s | Score: %s | Stale: %s", summary, result["score"], result["stale"])

        if result["severity"] in {"critical", "needs_update"}:
            suggestion = suggestion_text(ticket, result)
            print("\n" + suggestion + "\n")

        if result["severity"] == "critical":
            escalations.append({
                "number": ticket.get("number"),
                "priority": ticket.get("priority"),
                "score": result["score"],
                "summary": ticket.get("short_description", ""),
            })

    if escalations:
        logger.info("Escalating %d critical tickets", len(escalations))
        notify_lead(escalations)
    else:
        logger.info("No critical tickets to escalate")


def run_agent(interval: int = config.POLL_INTERVAL_SECONDS) -> None:
    excel_path = Path(config.EXCEL_FILE_PATH)

    logger.info("Starting ServiceNow ticket update listener")
    logger.info("Watching Excel source: %s", excel_path)
    logger.info("Polling every %s seconds", interval)

    last_mtime = None
    try:
        while True:
            if excel_path.exists():
                current_mtime = excel_path.stat().st_mtime
                if last_mtime is None or current_mtime != last_mtime:
                    last_mtime = current_mtime
                    logger.info("Detected change in Excel source; processing tickets")
                    process_tickets()
                else:
                    logger.debug("Excel file unchanged; waiting for next poll")
            else:
                if last_mtime is not None:
                    logger.warning("Excel source missing: %s", excel_path)
                    last_mtime = None
                logger.info("Excel file not found; processing fallback sample data")
                process_tickets()

            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("Agent stopped by user")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ServiceNow ticket update agent")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Process tickets once and exit instead of running continuously",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=config.POLL_INTERVAL_SECONDS,
        help="Polling interval in seconds when watching the Excel file",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.once:
        logger.info("Running a single ticket processing pass")
        process_tickets()
    else:
        run_agent(interval=args.interval)


if __name__ == "__main__":
    main()
