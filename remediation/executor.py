"""
Remediation executor.
Takes a TriageResult and runs the appropriate automated response.
"""
from dataclasses import dataclass
from datetime import datetime

from triage.llm_engine import TriageResult
from remediation.actions import ACTION_MAP, _write_incident_report


@dataclass
class RemediationResult:
    incident_id: str
    action_taken: str
    action_result: dict
    report_path: str
    executed_at: str
    sox_escalated: bool


def execute_remediation(triage: TriageResult) -> RemediationResult:
    triage_dict = triage.to_dict()
    action_key = triage.remediation_action

    print(f"\n{'='*60}")
    print(f"  INCIDENT TRIAGE RESULT")
    print(f"  Severity : {triage.severity}")
    print(f"  Category : {triage.category}")
    print(f"  Title    : {triage.title}")
    print(f"  SOX Risk : {'YES' if triage.sox_risk else 'No'}")
    print(f"  Action   : {action_key}")
    print(f"{'='*60}\n")

    action_fn = ACTION_MAP.get(action_key, ACTION_MAP["monitor_only"])
    action_result = action_fn(triage_dict)

    sox_escalated = False
    if triage.sox_risk and action_key != "page_oncall":
        print(f"  [SOX] Compliance risk detected — escalating to oncall")
        ACTION_MAP["page_oncall"](triage_dict)
        sox_escalated = True

    report_path = _write_incident_report(action_key, action_result, triage_dict)
    print(f"\n  Incident report saved: {report_path}")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return RemediationResult(
        incident_id=f"INC-{ts}",
        action_taken=action_key,
        action_result=action_result,
        report_path=report_path,
        executed_at=datetime.now().isoformat(),
        sox_escalated=sox_escalated,
    )