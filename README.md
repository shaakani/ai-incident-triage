# 🚨 AI-Powered Incident Triage System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Claude Sonnet](https://img.shields.io/badge/LLM-Claude%20Sonnet-orange.svg)](https://www.anthropic.com/)
[![Streamlit](https://img.shields.io/badge/dashboard-Streamlit-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> An end-to-end production support automation system that ingests error logs, uses Claude (LLM) to diagnose incidents, and triggers automated remediation — designed for Payments, Billing, and Finance platforms.

---

## What it does
Error Logs → Log Parser → Claude LLM Triage → Remediation Executor → Incident Report

1. **Ingests** raw log files from Payments, Billing, Collections, and Finance services
2. **Diagnoses** root cause, severity (P1–P4), blast radius, and SOX compliance risk using Claude
3. **Executes** automated remediation — pod restarts, scaling, DBA escalation, on-call paging
4. **Persists** structured incident reports for audit trails and post-mortems

---

## Demo

### CLI
```bash
python main.py --log logs/payment_errors.log
```

### Output
Parsed 7 log entries from payment_errors.log

Services: payments-service, billing-service, collections-agent, k8s
Severity : P1

Category : database

Title    : Payment Settlement Batch Failing Due to DB Outage and OOM

SOX Risk : YES

Confidence : 91%

Action   : page_oncall
Incident report saved: incidents/INC-20260616_222253-P1.json

---

## Project Structure

ai-incident-triage/

├── triage/

│   ├── log_parser.py      # Log ingestion & normalisation

│   └── llm_engine.py      # Claude API integration & structured triage

├── remediation/

│   ├── actions.py         # Remediation action library

│   └── executor.py        # Action selection & execution

├── dashboard/

│   └── app.py             # Streamlit live dashboard

├── logs/

│   ├── payment_errors.log       # Oracle DB timeout + OOM kill scenario

│   ├── fraud_spike.log          # Fraud detection anomaly scenario

│   └── db_replication_lag.log   # SOX audit trail failure scenario

├── tests/

│   ├── test_parser.py     # Log parser unit tests

│   └── test_triage.py     # Triage engine unit tests (mocked)

├── conftest.py            # Pytest configuration

├── main.py                # CLI entry point

├── requirements.txt

├── .env.example

└── .gitignore

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Claude Sonnet (Anthropic) |
| Language | Python 3.11+ |
| Dashboard | Streamlit |
| CLI output | Rich |
| Testing | Pytest |
| Log targets | Payments, Billing, Finance, Fraud, Airflow |
| Databases covered | Oracle PL/SQL, MongoDB |

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/shaakani/ai-incident-triage.git
cd ai-incident-triage

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your Anthropic API key
cp .env.example .env
# Edit .env and add your key: ANTHROPIC_API_KEY=sk-ant-...

# 5. Run triage on a sample log
python main.py --log logs/payment_errors.log

# 6. Launch the dashboard
streamlit run dashboard/app.py
```

---

## Sample Scenarios

| Log file | Scenario | Expected triage |
|---|---|---|
| `logs/payment_errors.log` | Oracle DB timeout + OOM kill | P1 · page_oncall · SOX risk |
| `logs/fraud_spike.log` | Fraud detection anomaly + Kafka lag | P1 · page_oncall |
| `logs/db_replication_lag.log` | SOX audit trail write failure | P1 · escalate_dba · SOX risk |

---

## Triage Output Schema

```json
{
  "severity": "P1",
  "category": "database",
  "title": "Payment Settlement Batch Failing Due to DB Outage and OOM",
  "summary": "...",
  "root_cause_hypothesis": "...",
  "blast_radius": "...",
  "remediation_action": "page_oncall",
  "remediation_rationale": "...",
  "sox_risk": true,
  "confidence": 0.91,
  "affected_services": ["payments-service", "billing-service"]
}
```

---

## Remediation Actions

| Action | When triggered |
|---|---|
| `restart_service` | Application crash, unresponsive pod |
| `scale_pods` | OOM kill, memory pressure, high load |
| `clear_cache` | Cache corruption, stale data |
| `page_oncall` | P1 incidents, multi-system failures |
| `escalate_dba` | Database replication lag, query failures |
| `trigger_failover` | Primary DB down, DR scenario |
| `monitor_only` | Warnings, low severity issues |

---

## Running Tests

```bash
pytest tests/ -v
```

Expected output: **8 passed**

---

## How this maps to Production Support Engineering

| JD Requirement | This project |
|---|---|
| Incident response & triage | Automated log → diagnosis → action pipeline |
| AI/ML in production ops | LLM-based root cause analysis and decision making |
| Observability tooling | Structured parsing of Splunk/Grafana format logs |
| SOX compliance | Auto-detection and escalation of compliance risk |
| Payments & Finance platforms | Scenarios cover Oracle, MongoDB, Kafka, Airflow |
| Automation & MTTR reduction | Auto-remediation reduces manual intervention |

---

## License

MIT