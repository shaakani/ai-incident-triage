"""
Remediation action implementations.
"""
import json
from datetime import datetime
from pathlib import Path

INCIDENT_DIR = Path("incidents")


def _write_incident_report(action: str, result: dict, triage: dict) -> str:
    """Save incident to MongoDB and also keep a local JSON backup."""
    # Save to MongoDB
    try:
        from storage.mongo_store import save_incident
        incident_id = save_incident(action, result, triage)
    except Exception as e:
        print(f"  [MongoDB] Warning: could not save to MongoDB: {e}")
        incident_id = f"INC-{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Keep local JSON backup as well
    INCIDENT_DIR.mkdir(exist_ok=True)
    filename = INCIDENT_DIR / f"{incident_id}-{triage.get('severity','P2')}.json"
    report = {
        "incident_id": incident_id,
        "created_at": datetime.now().isoformat(),
        "triage": triage,
        "action_taken": action,
        "action_result": result,
    }
    filename.write_text(json.dumps(report, indent=2))
    return str(filename)


def restart_service(triage: dict) -> dict:
    services = triage.get("affected_services", ["unknown-service"])
    print(f"  [ACTION] Sending restart signal to: {', '.join(services)}")
    return {
        "status": "executed",
        "action": "restart_service",
        "targets": services,
        "command": f"kubectl rollout restart deployment/{services[0]} -n production",
        "note": "Simulated — no live cluster connected",
    }


def scale_pods(triage: dict) -> dict:
    services = triage.get("affected_services", ["unknown-service"])
    print(f"  [ACTION] Scaling up pods for: {', '.join(services)}")
    return {
        "status": "executed",
        "action": "scale_pods",
        "targets": services,
        "replicas": 6,
        "command": f"kubectl scale deployment/{services[0]} --replicas=6 -n production",
        "note": "Simulated — no live cluster connected",
    }


def clear_cache(triage: dict) -> dict:
    print(f"  [ACTION] Clearing application cache")
    return {
        "status": "executed",
        "action": "clear_cache",
        "note": "Simulated cache flush — Redis FLUSHDB would be called in production",
    }


def page_oncall(triage: dict) -> dict:
    severity = triage.get("severity", "P2")
    title = triage.get("title", "Production incident")
    print(f"  [ACTION] Paging on-call engineer — {severity}: {title}")
    return {
        "status": "executed",
        "action": "page_oncall",
        "severity": severity,
        "message": f"ALERT [{severity}] {title}",
        "channel": "PagerDuty (simulated)",
        "note": "Simulated — configure PAGERDUTY_TOKEN in .env for live alerts",
    }


def escalate_dba(triage: dict) -> dict:
    print(f"  [ACTION] Escalating to DBA team via Slack #dba-oncall")
    return {
        "status": "executed",
        "action": "escalate_dba",
        "channel": "Slack #dba-oncall (simulated)",
        "note": "Simulated — configure SLACK_WEBHOOK in .env for live alerts",
    }


def trigger_failover(triage: dict) -> dict:
    print(f"  [ACTION] Initiating database failover procedure")
    return {
        "status": "executed",
        "action": "trigger_failover",
        "note": "Simulated — in production this triggers DR runbook automation",
    }


def monitor_only(triage: dict) -> dict:
    print(f"  [ACTION] No automated action — escalated to monitoring dashboard")
    return {
        "status": "monitoring",
        "action": "monitor_only",
        "note": "Incident logged for human review",
    }


ACTION_MAP = {
    "restart_service": restart_service,
    "scale_pods": scale_pods,
    "clear_cache": clear_cache,
    "page_oncall": page_oncall,
    "escalate_dba": escalate_dba,
    "trigger_failover": trigger_failover,
    "monitor_only": monitor_only,
}