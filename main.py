"""
AI-Powered Incident Triage System
Entry point for CLI usage.

Usage:
  python main.py --log logs/samples/payment_errors.log
  python main.py --log logs/samples/fraud_spike.log
"""
import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from triage.log_parser import parse_log_file
from triage.llm_engine import triage_logs
from remediation.executor import execute_remediation

console = Console()

SEVERITY_COLORS = {"P1": "red", "P2": "yellow", "P3": "cyan", "P4": "green"}


def run_triage(log_path: str):
    path = Path(log_path)
    if not path.exists():
        console.print(f"[red]Error: log file not found: {log_path}[/red]")
        sys.exit(1)

    console.rule("[bold]AI Incident Triage System[/bold]")

    # Step 1: Parse logs
    with console.status(f"[cyan]Parsing logs from {path.name}...[/cyan]"):
        bundle = parse_log_file(path)

    console.print(f"✓ Parsed [bold]{len(bundle.entries)}[/bold] log entries from [cyan]{bundle.source}[/cyan]")
    console.print(f"  Services: {', '.join(bundle.affected_services)}")
    console.print(f"  Errors: {bundle.error_count}  Criticals: {bundle.critical_count}\n")

    # Step 2: LLM triage
    with console.status("[yellow]Running AI triage analysis...[/yellow]"):
        triage = triage_logs(bundle)

    color = SEVERITY_COLORS.get(triage.severity, "white")

    # Display triage result
    table = Table(box=box.ROUNDED, show_header=False, padding=(0, 1))
    table.add_column("Field", style="dim", width=22)
    table.add_column("Value")
    table.add_row("Severity", f"[bold {color}]{triage.severity}[/bold {color}]")
    table.add_row("Category", triage.category)
    table.add_row("Title", f"[bold]{triage.title}[/bold]")
    table.add_row("Summary", triage.summary)
    table.add_row("Root cause", triage.root_cause_hypothesis)
    table.add_row("Blast radius", triage.blast_radius)
    table.add_row("SOX risk", "[bold red]YES[/bold red]" if triage.sox_risk else "No")
    table.add_row("Confidence", f"{triage.confidence:.0%}")
    table.add_row("Recommended action", f"[bold yellow]{triage.remediation_action}[/bold yellow]")
    table.add_row("Rationale", triage.remediation_rationale)

    console.print(Panel(table, title="[bold]Triage Report[/bold]", border_style=color))

    # Step 3: Execute remediation
    console.print("\n[bold]Executing remediation...[/bold]")
    result = execute_remediation(triage)

    console.print(f"\n[green]✓ Done.[/green] Incident ID: [bold]{result.incident_id}[/bold]")
    console.print(f"  Report: {result.report_path}")
    if result.sox_escalated:
        console.print("[bold red]  ⚠️  SOX compliance escalation triggered[/bold red]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI-powered incident triage system")
    parser.add_argument("--log", required=True, help="Path to the log file to triage")
    args = parser.parse_args()
    run_triage(args.log)