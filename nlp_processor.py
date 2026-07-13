import re

NEGATIVE_KEYWORDS = {
    "urgent",
    "immediately",
    "critical",
    "down",
    "blocked",
    "failed",
    "not working",
    "timeout",
    "error",
    "issue",
    "unable",
}
POSITIVE_KEYWORDS = {
    "working",
    "resolved",
    "successful",
    "completed",
    "available",
    "restored",
}
HIGH_URGENCY_KEYWORDS = {
    "urgent",
    "asap",
    "immediately",
    "right away",
    "critical",
    "severe",
    "down",
    "outage",
}
INTENT_KEYWORDS = {
    "blocked": ["blocked", "blocking", "blocked by"],
    "failed": ["failed", "failure", "unable to"],
    "not_working": ["not working", "does not work", "cannot use", "can't use"],
    "reopen": ["reopen", "re-open"],
}


def normalize_text(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.strip().lower())


def detect_sentiment(text: str) -> str:
    normalized = normalize_text(text)
    negative = sum(1 for token in NEGATIVE_KEYWORDS if token in normalized)
    positive = sum(1 for token in POSITIVE_KEYWORDS if token in normalized)
    if negative >= max(2, positive + 1):
        return "negative"
    if positive > negative:
        return "positive"
    return "neutral"


def detect_urgency(text: str) -> str:
    normalized = normalize_text(text)
    if any(token in normalized for token in HIGH_URGENCY_KEYWORDS):
        return "high"
    return "normal"


def detect_intent(text: str) -> str:
    normalized = normalize_text(text)
    for intent, phrases in INTENT_KEYWORDS.items():
        for phrase in phrases:
            if phrase in normalized:
                return intent
    return "informational"


def extract_user_concern(text: str) -> str:
    normalized = normalize_text(text)
    if "vpn" in normalized:
        return "VPN connectivity issue"
    if "email" in normalized:
        return "Email delivery or access problem"
    if "network" in normalized or "internet" in normalized:
        return "Network or connectivity problem"
    if "login" in normalized or "sign in" in normalized:
        return "Authentication or login failure"
    if "server" in normalized or "database" in normalized:
        return "Server or database availability issue"
    if "application" in normalized or "app" in normalized:
        return "Application functionality issue"
    return "Unspecified user concern"


def analyze_ticket_text(short_description: str, description: str, comments: str, activity_logs: str = "") -> dict:
    combined_text = " ".join(
        part for part in (short_description, description, comments, activity_logs) if part
    )
    return {
        "sentiment": detect_sentiment(combined_text),
        "urgency": detect_urgency(combined_text),
        "intent": detect_intent(combined_text),
        "concern": extract_user_concern(combined_text),
        "summary": normalize_text(combined_text),
    }
