import pytest
from triage.log_parser import parse_log_text, ParsedLogBundle

SAMPLE_LOG = """2024-06-15 02:14:33 ERROR [payments-service] DB connection timeout after 30s
2024-06-15 02:14:35 CRITICAL [payments-service] Failed to process settlement batch
2024-06-15 02:15:01 ERROR [billing-service] MongoDB write timeout on collection=invoices
2024-06-15 02:15:12 WARN  [collections-agent] 3 retries exhausted for customer_id=CUS-88821
"""

def test_parse_returns_bundle():
    bundle = parse_log_text(SAMPLE_LOG)
    assert isinstance(bundle, ParsedLogBundle)

def test_parse_entry_count():
    bundle = parse_log_text(SAMPLE_LOG)
    assert len(bundle.entries) == 4

def test_parse_highest_severity():
    bundle = parse_log_text(SAMPLE_LOG)
    assert bundle.highest_severity == "CRITICAL"

def test_parse_affected_services():
    bundle = parse_log_text(SAMPLE_LOG)
    assert "payments-service" in bundle.affected_services
    assert "billing-service" in bundle.affected_services

def test_parse_error_counts():
    bundle = parse_log_text(SAMPLE_LOG)
    assert bundle.error_count == 2
    assert bundle.critical_count == 1

def test_parse_empty_log():
    bundle = parse_log_text("")
    assert len(bundle.entries) == 0
    assert bundle.highest_severity == "NONE"

def test_context_string_format():
    bundle = parse_log_text(SAMPLE_LOG)
    ctx = bundle.to_context_string()
    assert "payments-service" in ctx
    assert "Log source" in ctx