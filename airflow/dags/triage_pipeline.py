"""
Airflow DAG — AI Incident Triage Pipeline
Scans the logs folder every 5 minutes and runs triage on any .log files found.
"""
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

from airflow.decorators import dag, task

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@dag(
    dag_id="ai_incident_triage_pipeline",
    description="Scans payment logs and runs AI triage automatically",
    schedule="*/5 * * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["payments", "triage", "production-support"],
)
def triage_pipeline():

    @task()
    def scan_logs() -> list[str]:
        """Scan the logs folder for .log files."""
        logs_dir = PROJECT_ROOT / "logs"
        log_files = list(logs_dir.glob("*.log"))
        print(f"Found {len(log_files)} log files: {[f.name for f in log_files]}")
        return [str(f) for f in log_files]

    @task()
    def run_triage(log_files: list[str]) -> list[dict]:
        """Run AI triage on each log file."""
        from dotenv import load_dotenv
        load_dotenv(PROJECT_ROOT / ".env")

        from triage.log_parser import parse_log_file
        from triage.llm_engine import triage_logs

        results = []
        for log_path in log_files:
            print(f"Triaging: {log_path}")
            bundle = parse_log_file(log_path)
            if not bundle.entries:
                print(f"No entries found in {log_path}, skipping")
                continue
            triage = triage_logs(bundle)
            results.append({
                "file": log_path,
                "severity": triage.severity,
                "title": triage.title,
                "action": triage.remediation_action,
                "sox_risk": triage.sox_risk,
            })
            print(f"Triage complete: {triage.severity} — {triage.title}")
        return results

    @task()
    def execute_remediation(triage_results: list[dict]) -> None:
        """Log remediation summary."""
        print(f"\n{'='*50}")
        print(f"TRIAGE PIPELINE COMPLETE")
        print(f"Processed {len(triage_results)} incidents")
        for r in triage_results:
            print(f"  [{r['severity']}] {r['title']}")
            print(f"    Action: {r['action']} | SOX: {r['sox_risk']}")
        print(f"{'='*50}")

    logs = scan_logs()
    results = run_triage(logs)
    execute_remediation(results)


triage_pipeline()