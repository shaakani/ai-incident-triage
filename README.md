# 🚨 AI-Powered Incident Triage System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Claude Sonnet](https://img.shields.io/badge/LLM-Claude%20Sonnet-orange.svg)](https://www.anthropic.com/)
[![Streamlit](https://img.shields.io/badge/dashboard-Streamlit-red.svg)](https://streamlit.io/)
[![Airflow](https://img.shields.io/badge/orchestration-Airflow-017CEE.svg)](https://airflow.apache.org/)
[![MongoDB](https://img.shields.io/badge/database-MongoDB-47A248.svg)](https://www.mongodb.com/)
[![Grafana](https://img.shields.io/badge/monitoring-Grafana-F46800.svg)](https://grafana.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> An end-to-end production incident response platform that reads error logs, uses Claude LLM to diagnose issues, executes automated remediation, stores incidents in MongoDB, visualises trends in Grafana, and runs on a scheduled Airflow pipeline.

---

## What it does

Error Logs → Log Parser → Claude LLM Triage → Remediation Executor → MongoDB → Grafana

1. **Ingests** raw log files from Payments, Billing, Collections, and Finance services
2. **Diagnoses** root cause, severity (P1–P4), blast radius, and SOX compliance risk using Claude
3. **Executes** automated remediation — pod restarts, scaling, DBA escalation, on-call paging
4. **Stores** every incident in MongoDB for querying and audit trails
5. **Visualises** incident trends and severity breakdown in Grafana
6. **Schedules** the full pipeline automatically every 5 minutes via Apache Airflow

---

## Architecture

ai-incident-triage/

├── triage/
│   ├── log_parser.py       # Log ingestion & normalisation
│   └── llm_engine.py       # Claude API — structured triage output
├── remediation/
│   ├── actions.py          # 7 remediation action types
│   └── executor.py         # Action selection & execution
├── storage/
│   └── mongo_store.py      # MongoDB persistence layer
├── dashboard/
│   └── app.py              # Streamlit live dashboard
├── airflow/
│   └── dags/
│       └── triage_pipeline.py  # Airflow DAG — runs every 5 mins
├── grafana/
│   └── dashboard.json      # Grafana operations dashboard
├── scripts/
│   ├── setup.sh            # One-command project setup
│   └── watch_logs.sh       # Auto-trigger triage on new log files
├── logs/                   # Sample Payments/Finance error scenarios
├── tests/                  # 8 unit tests
├── Makefile                # One-command shortcuts
└── main.py                 # CLI entry point

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Claude Sonnet (Anthropic API) |
| Language | Python 3.11+ |
| Dashboard | Streamlit |
| Orchestration | Apache Airflow |
| Database | MongoDB + pymongo |
| Monitoring | Grafana |
| CLI | Rich |
| Testing | Pytest |

---

## Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/shaakani/ai-incident-triage.git
cd ai-incident-triage
make setup

# 2. Add your Anthropic API key
echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env

# 3. Run triage on a sample log
make run

# 4. Launch the dashboard
make dashboard

# 5. Start Airflow scheduler
make airflow

# 6. Watch for new logs automatically
make watch
```

---

## Sample Scenarios

| Log file | Scenario | Triage output |
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

## Makefile Commands

```bash
make setup      # Install dependencies and set up project
make run        # Triage the sample payment_errors.log
make triage LOG=logs/fraud_spike.log   # Triage any log file
make test       # Run all 8 unit tests
make dashboard  # Launch Streamlit dashboard
make airflow    # Start Airflow scheduler
make watch      # Watch logs folder for new files
```

---

## Running Tests

```bash
pytest tests/ -v
# Expected: 8 passed
```

---

## How this maps to Production Support Engineering

| JD Requirement | This project |
|---|---|
| Incident response & triage | Automated log → diagnosis → action pipeline |
| AI/ML in production ops | LLM-based root cause analysis and decision making |
| Apache Airflow | Scheduled DAG running every 5 minutes |
| MongoDB / NoSQL | Full incident persistence with querying |
| Observability tooling | Grafana dashboard with live incident metrics |
| SOX compliance | Auto-detection and escalation of compliance risk |
| Payments & Finance platforms | Oracle, MongoDB, Kafka, Airflow error scenarios |
| Shell scripting & Linux | Bash scripts and Makefile automation |
| Automation & MTTR reduction | End-to-end pipeline with no manual steps |

---

## License

MIT