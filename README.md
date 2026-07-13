# ServiceNow Ticket Update Agent

A Python listener agent that watches an Excel file for ServiceNow-like ticket data, identifies open tickets needing attention, suggests updates, escalates critical issues, and provides a Streamlit dashboard for monitoring.

---

## What this project does

- Watches a configured Excel file continuously.
- Reads open ticket rows from Excel.
- Applies simple NLP-style analysis on ticket descriptions and comments.
- Scores ticket criticality using priority, staleness, sentiment, urgency, and intent.
- Prints suggested ticket updates for tickets requiring attention.
- Prints critical escalation summaries for lead review.
- Displays dashboard metrics, flagged tickets, and resolution history.
- Falls back to sample data when Excel is unavailable.

---

## Project structure

```
.
+-- analyzer.py
+-- config.py
+-- dashboard.py
+-- escalation.py
+-- fetcher.py
+-- main.py
+-- nlp_processor.py
+-- README.md
+-- requirements.txt
+-- suggestion_engine.py
+-- tracker.py
+-- utils.py
```

---

## Components

- `main.py`
  - Runs the listener loop.
  - Polls the Excel file for changes.
  - Processes ticket rows when the file changes.

- `dashboard.py`
  - Provides a Streamlit dashboard for metrics and live ticket status.

- `tracker.py`
  - Maintains history and metrics for tickets resolved after being flagged.

- `config.py`
  - Contains Excel source settings and thresholds.
  - Defines polling interval and fallback behavior.

- `fetcher.py`
  - Reads ticket rows from the configured Excel file.
  - Supports a fallback sample dataset.

- `nlp_processor.py`
  - Detects sentiment, urgency, intent, and concern from ticket text.

- `analyzer.py`
  - Computes ticket staleness and criticality scores.

- `suggestion_engine.py`
  - Generates suggested update text for tickets.

- `escalation.py`
  - Prints critical escalation summaries instead of sending real alerts.

- `utils.py`
  - Helper formatting functions.

---

## Data source

The agent supports a single ticket source:

- `tickets.xlsx` — local Excel file.

The agent reads `tickets.xlsx` and falls back to sample data only if the Excel file is unavailable.

`activity_logs` is supported as an optional column and can be used for additional ticket context.

### Required columns

The ticket file should include these columns in the first row:

- `number`
- `short_description`
- `description`
- `priority`
- `state`
- `sys_updated_on`
- `sys_created_on`
- `comments`

Column aliases are supported, such as `summary` → `short_description` and `updated_on` → `sys_updated_on`.

Open ticket rows should use a state other than `closed`, `resolved`, `cancelled`, or `canceled`.

---

## Configuration

Key settings in `config.py`:

- `EXCEL_FILE_PATH` � path to the Excel file to watch.
- `POLL_INTERVAL_SECONDS` � how often the agent checks for file changes.
- `STALE_THRESHOLD_HOURS` � hours before a ticket becomes stale.
- `CRITICAL_THRESHOLD` � score threshold for escalation.

---

## Running the listener

Install dependencies:

```bash
pip install -r requirements.txt
```

Then run:

```bash
python main.py --once
```

The agent will process the Excel file once and exit.

To run continuously and watch for file changes:

```bash
python main.py
```

The agent will poll the Excel file and process tickets whenever the file is updated.

---

## Running the dashboard

Install dependencies:

```bash
pip install -r requirements.txt
```

Then run:

```bash
streamlit run dashboard.py
```

Open the URL shown by Streamlit in your browser to view live ticket metrics and suggestions.

---

## Ticket analysis

### Sentiment

Detects negative terms such as:
- `urgent`
- `down`
- `blocked`
- `failed`
- `error`

### Urgency

Detects high urgency from words like:
- `urgent`
- `asap`
- `immediately`
- `critical`
- `down`
- `outage`

### Intent

Detects issue intent such as:
- `blocked`
- `failed`
- `not_working`
- `informational`

### Concern extraction

Maps text to common issue categories such as VPN, email, network, login, server/database, and application issues.

---

## Criticality scoring

Score contributions:

- Priority 1 or 2 ? +3
- Priority 3 ? +1
- Stale ticket ? +2
- Negative sentiment ? +2
- High urgency ? +2
- Blocked/failed/not working intent ? +3

Severity levels:

- `critical` � score >= `CRITICAL_THRESHOLD`
- `needs_update` � score >= 3 or ticket is stale
- `monitor` � otherwise

---

## Dependencies

- `openpyxl`
- `streamlit`

---

## Future extension

When ServiceNow is hooked up, the same analysis flow can be reused by replacing `fetcher.py` with a ServiceNow API connector.

---

## Notes

- The current agent uses Excel as the data source.
- It watches the file and reprocesses tickets on each change.
- Critical escalations are printed rather than sent.
