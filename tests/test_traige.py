import pytest
from unittest.mock import MagicMock, patch
from triage.log_parser import parse_log_text
from triage.llm_engine import triage_logs, TriageResult

SAMPLE_LOG = """2024-06-15 02:14:33 CRITICAL [payments-service] OOMKilled: container exceeded memory limit
"""

MOCK_LLM_RESPONSE = """{
  "severity": "P1",
  "category": "memory",
  "title": "Payments service OOM kill in production",
  "summary": "The payments-service container was killed by the OOM killer after exceeding its 2Gi memory limit.",
  "root_cause_hypothesis": "Memory leak in payments-worker causing unbounded heap growth.",
  "blast_radius": "All in-flight payment transactions may be lost. Settlement batch at risk.",
  "remediation_action": "scale_pods",
  "remediation_rationale": "Scaling pods redistributes load while root cause is investigated.",
  "confidence": 0.88,
  "affected_services": ["payments-service"],
  "sox_risk": true
}"""

def test_triage_returns_result():
    bundle = parse_log_text(SAMPLE_LOG)
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=MOCK_LLM_RESPONSE)]

    with patch("triage.llm_engine.anthropic.Anthropic") as MockClient:
        MockClient.return_value.messages.create.return_value = mock_message
        result = triage_logs(bundle)

    assert isinstance(result, TriageResult)
    assert result.severity == "P1"
    assert result.category == "memory"
    assert result.sox_risk is True
    assert result.remediation_action == "scale_pods"
    assert result.confidence == 0.88