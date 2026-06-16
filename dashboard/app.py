import json
import os
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))
load_dotenv(Path(__file__).parent.parent / ".env")

from triage.log_parser import parse_log_text
from triage.llm_engine import triage_logs
from remediation.executor import execute_remediation

st.set_page_config(page_title="AI Incident Triage", page_icon="🚨", layout="wide")

SAMPLE_LOGS_DIR = Path(__file__).parent.parent / "logs"

if "log_text" not in st.session_state:
    st.session_state["log_text"] = ""
if "log_source" not in st.session_state:
    st.session_state["log_source"] = "dashboard_input"
if "triage_result" not in st.session_state:
    st.session_state["triage_result"] = None
if "last_result" not in st.session_state:
    st.session_state["last_result"] = None

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🚨 AI Incident Triage")
    st.caption("Powered by Claude · Built for Payments Ops")
    st.divider()

    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        value=os.getenv("ANTHROPIC_API_KEY", ""),
    )
    if api_key:
        os.environ["ANTHROPIC_API_KEY"] = api_key

    st.divider()
    st.markdown("**Quick load sample logs:**")
    sample_files = list(SAMPLE_LOGS_DIR.glob("*.log")) if SAMPLE_LOGS_DIR.exists() else []

    for sf in sample_files:
        if st.button(f"📄 {sf.name}", use_container_width=True):
            st.session_state["log_text"] = sf.read_text()
            st.session_state["log_source"] = sf.name
            st.session_state["triage_result"] = None
            st.session_state["last_result"] = None
            st.rerun()

# ── Main area ─────────────────────────────────────────────────────────────────
st.header("Log Input")
col1, col2 = st.columns([3, 1])

with col1:
    displayed_text = st.text_area(
        "Paste error logs here (or load a sample from the sidebar)",
        value=st.session_state["log_text"],
        height=220,
        placeholder="2024-06-15 02:14:33 ERROR [payments-service] DB connection timeout...",
    )

with col2:
    st.markdown("<br>" * 3, unsafe_allow_html=True)
    run_btn = st.button(
        "🔍 Run Triage",
        type="primary",
        use_container_width=True,
    )
    if not api_key:
        st.warning("Add API key in sidebar")

# ── Run triage ────────────────────────────────────────────────────────────────
if run_btn:
    log_content = displayed_text or st.session_state["log_text"]

    if not log_content:
        st.error("Please load a sample log or paste log content first.")
    elif not api_key:
        st.error("Please add your Anthropic API key in the sidebar.")
    else:
        with st.spinner("Parsing logs..."):
            bundle = parse_log_text(log_content, source=st.session_state["log_source"])

        if not bundle.entries:
            st.error("No parseable log entries found.")
        else:
            st.success(f"Parsed {len(bundle.entries)} entries from {len(bundle.affected_services)} services")

            with st.spinner("Running AI triage analysis..."):
                try:
                    triage = triage_logs(bundle)
                    st.session_state["triage_result"] = triage
                except Exception as e:
                    st.error(f"Triage failed: {e}")

# ── Show triage result ────────────────────────────────────────────────────────
if st.session_state["triage_result"]:
    triage = st.session_state["triage_result"]

    st.divider()
    st.subheader("Triage Report")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Severity", triage.severity)
    m2.metric("Category", triage.category.replace("_", " ").title())
    m3.metric("Confidence", f"{triage.confidence:.0%}")
    m4.metric("SOX Risk", "⚠️ YES" if triage.sox_risk else "✅ No")

    st.markdown(f"### {triage.title}")
    st.info(triage.summary)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Root cause hypothesis**")
        st.write(triage.root_cause_hypothesis)
        st.markdown("**Blast radius**")
        st.write(triage.blast_radius)
    with col_b:
        st.markdown("**Recommended action**")
        st.code(triage.remediation_action)
        st.markdown("**Rationale**")
        st.write(triage.remediation_rationale)

    st.divider()
    st.subheader("Automated Remediation")

    if st.button(f"⚡ Execute: `{triage.remediation_action}`", type="primary"):
        with st.spinner("Executing remediation..."):
            result = execute_remediation(triage)
        st.session_state["last_result"] = {
            "incident_id": result.incident_id,
            "action_result": result.action_result,
            "sox_escalated": result.sox_escalated,
            "report_path": result.report_path,
        }

    if st.session_state["last_result"]:
        r = st.session_state["last_result"]
        st.success(f"✅ Done · Incident ID: `{r['incident_id']}`")
        st.json(r["action_result"])
        if r["sox_escalated"]:
            st.warning("⚠️ SOX compliance escalation triggered — on-call paged")
        if Path(r["report_path"]).exists():
            report_data = Path(r["report_path"]).read_text()
            st.download_button(
                "📥 Download incident report",
                data=report_data,
                file_name=f"{r['incident_id']}.json",
                mime="application/json",
            )

# ── Incident history ──────────────────────────────────────────────────────────
incident_dir = Path("incidents")
if incident_dir.exists():
    incidents = sorted(incident_dir.glob("*.json"), reverse=True)
    if incidents:
        st.divider()
        st.subheader(f"Incident History ({len(incidents)} incidents)")
        for inc_file in incidents[:10]:
            data = json.loads(inc_file.read_text())
            t = data["triage"]
            with st.expander(f"{inc_file.stem} — {t.get('title','Unknown')} [{t.get('severity','?')}]"):
                st.json(data)