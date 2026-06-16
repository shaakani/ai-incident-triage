"""
LLM-powered triage engine.
Sends parsed log context to Claude and returns a structured TriageResult.
"""
import json
import os
from dataclasses import dataclass
from datetime import datetime

import anthropic
from dotenv import load_dotenv

from triage.log_parser import ParsedLogBundle

load_dotenv()

TRIAGE_SYSTEM_PROMPT = """You are an expert production support engineer specialising in Payments, Billing, and Finance platforms.
You analyse error logs and produce structured incident triage reports.

Always respond with a single valid JSON object — no markdown, no explanation outside the JSON.

Your JSON must follow this exact schema:
{
  "severity": "P1" | "P2" | "P3" | "P4",
  "category": "database" | "memory" | "network" | "fraud" | "compliance" | "performance" | "application" | "infrastructure",
  "title": "short incident title (max 10 words)",
  "summary": "2-3 sentence plain-English summary of what is happening",
  "root_cause_hypothesis": "most likely root cause based on the log evidence",
  "blast_radius": "what is at risk if not addressed immediately",
  "remediation_action": "restart_service" | "scale_pods" | "clear_cache" | "page_oncall" | "escalate_dba" | "trigger_failover" | "monitor_only",
  "remediation_rationale": "1 sentence explaining why this remediation was chosen",
  "confidence": 0.0-1.0,
  "affected_services": ["list", "of", "service", "names"],
  "sox_risk": true | false
}

Severity guide:
- P1: Production down, revenue impact, SOX/compliance risk
- P2: Degraded service, elevated error rate, risk of escalation
- P3: Non-critical errors, isolated failures, monitoring needed
- P4: Warnings, no immediate action required
"""


@dataclass
class TriageResult:
    severity: str
    category: str
    title: str
    summary: str
    root_cause_hypothesis: str
    blast_radius: str
    remediation_action: str
    remediation_rationale: str
    confidence: float
    affected_services: list[str]
    sox_risk: bool
    triaged_at: str
    raw_llm_response: str

    def to_dict(self) -> dict:
        return self.__dict__


def triage_logs(bundle: ParsedLogBundle) -> TriageResult:
    """
    Send a parsed log bundle to Claude for AI-powered triage.
    Returns a structured TriageResult.
    """
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    user_message = f"""Please triage the following production logs:

{bundle.to_context_string()}

Respond only with the JSON triage report."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=TRIAGE_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw_response = message.content[0].text

    try:
        data = json.loads(raw_response)
    except json.JSONDecodeError:
        import re
        match = re.search(r"\{.*\}", raw_response, re.DOTALL)
        if match:
            data = json.loads(match.group())
        else:
            raise ValueError(f"LLM returned non-JSON response: {raw_response}")

    return TriageResult(
        severity=data.get("severity", "P2"),
        category=data.get("category", "application"),
        title=data.get("title", "Unknown incident"),
        summary=data.get("summary", ""),
        root_cause_hypothesis=data.get("root_cause_hypothesis", ""),
        blast_radius=data.get("blast_radius", ""),
        remediation_action=data.get("remediation_action", "monitor_only"),
        remediation_rationale=data.get("remediation_rationale", ""),
        confidence=float(data.get("confidence", 0.5)),
        affected_services=data.get("affected_services", bundle.affected_services),
        sox_risk=bool(data.get("sox_risk", False)),
        triaged_at=datetime.now().isoformat(),
        raw_llm_response=raw_response,
    )