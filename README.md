# **ServiceNow Ticket Update Agent**  
A lightweight Python-based automation agent that identifies stale ServiceNow tickets, analyzes user concerns using NLP, suggests meaningful updates, and escalates critical tickets to the Lead via Teams or email.

---

## **📌 Features**

- 🔄 **ServiceNow Integration**  
  Fetch active incidents using the ServiceNow REST API.

- 🕒 **Stale Ticket Detection**  
  Flags tickets with no updates beyond a configurable threshold.

- 🧠 **NLP-Based Analysis**  
  Extracts sentiment, urgency, and intent from ticket descriptions and comments.

- 🚨 **Criticality Scoring**  
  Combines priority, freshness, sentiment, urgency, and intent.

- ✍️ **Suggested Updates**  
  Auto-generates context-aware ticket updates.

- 📣 **Escalation Notifications**  
  Sends critical ticket summaries to Leads via Teams webhook or email.

- 🧩 **Minimal Architecture**  
  Easy to deploy as a cron job, Azure Function, or AWS Lambda.

---

## **📁 Project Structure**

```
servicenow-agent/
│
├── main.py
├── config.py
├── fetcher.py
├── analyzer.py
├── nlp_processor.py
├── suggestion_engine.py
├── escalation.py
├── utils.py
└── requirements.txt
```

---

## **⚙️ Architecture Overview**

### **High-Level Flow**

```
Scheduler
   ↓
ServiceNow API → Ticket Fetcher
   ↓
Ticket Analyzer → NLP Processor
   ↓
Suggestion Engine
   ↓
Escalation Module → Teams/Email
   ↓
(Optional) Dashboard
```

### **Core Components**

| Component | Responsibility |
|----------|----------------|
| `fetcher.py` | Connects to ServiceNow and retrieves tickets |
| `analyzer.py` | Applies freshness rules and base scoring |
| `nlp_processor.py` | Extracts sentiment, urgency, intent |
| `suggestion_engine.py` | Computes criticality & suggests updates |
| `escalation.py` | Sends notifications to Leads |
| `main.py` | Orchestrates the entire agent run |

---

## **🔧 Installation**

### **1. Clone the repository**
```bash
git clone https://github.com/<your-username>/servicenow-agent.git
cd servicenow-agent
```

### **2. Install dependencies**
```bash
pip install -r requirements.txt
```

### **3. Configure environment**
Edit `config.py`:

```python
SERVICENOW_URL = "https://<instance>.service-now.com/api/now/table/incident"
SERVICENOW_USER = "<username>"
SERVICENOW_PASSWORD = "<password>"

STALE_THRESHOLD_HOURS = 24
ESCALATION_EMAIL = "lead@example.com"
TEAMS_WEBHOOK_URL = "<teams_webhook>"
```

---

## **🚀 Running the Agent**

### **Local Run**
```bash
python main.py
```

### **Cron Job (Linux)**
Run every hour:
```bash
0 * * * * /usr/bin/python3 /path/to/main.py >> /var/log/servicenow_agent.log 2>&1
```

### **Azure Function**
Wrap `run_agent()` inside a timer-trigger function.

### **AWS Lambda**
Use CloudWatch Events to trigger the Lambda periodically.

---

## **🧠 NLP Logic**

### **Sentiment Analysis**
Using TextBlob polarity:
- `> 0.1` → positive  
- `< -0.1` → negative  
- otherwise → neutral  

### **Urgency Detection**
Keywords:
```
urgent, asap, immediately, down, critical
```

### **Intent Detection**
Keywords:
```
blocked, error, failed, not working
```

---

## **🔥 Criticality Scoring**

| Condition | Score |
|----------|-------|
| Priority 1–2 | +3 |
| Stale > 48 hours | +2 |
| Negative sentiment | +2 |
| Intent = blocked | +3 |
| High urgency | +2 |

### **Levels**
- **≥ 6** → Critical (Escalate)  
- **3–5** → Needs Update  
- **< 3** → Monitor  

---

## **📣 Escalation Example (Teams Webhook)**

```python
message = {
    "text": "Critical Ticket Escalation Report\nINC0012345 | VPN down | Score: 7"
}
requests.post(TEAMS_WEBHOOK_URL, json=message)
```

---

## **🧪 Sample ServiceNow API Call**

```python
import requests

url = "https://<instance>.service-now.com/api/now/table/incident"
params = {"sysparm_query": "active=true^priority<=3", "sysparm_limit": "10"}

response = requests.get(url, auth=(USERNAME, PASSWORD), params=params)
```

---

## **📜 Requirements**

```
requests
textblob
spacy
```

---

## **🛡️ Security**

- Store credentials in Azure Key Vault / AWS Secrets Manager.  
- Use read-only ServiceNow API roles.  
- Avoid logging sensitive ticket content.  

---

## **📅 Implementation Timeline**

| Week | Deliverables |
|------|--------------|
| Week 1 | API integration, freshness rules |
| Week 2 | NLP processor, suggestion engine |
| Week 3 | Escalation module, integration testing |
| Week 4 | Optimization, dashboard (optional), deployment |

---

## **🤝 Contributing**

Pull requests are welcome.  
For major changes, open an issue first to discuss what you’d like to modify.

---

## **📄 License**

MIT License (or your preferred license).

---

## **💬 Support**

For questions or enhancements, contact:  
**Ramkumar – IT Project/Technical Manager**

---

If you want, I can also generate:

- A **Dockerfile**  
- A **GitHub Actions CI/CD pipeline**  
- A **project wiki**  
- A **sample dashboard UI**  

Just tell me what you want next.