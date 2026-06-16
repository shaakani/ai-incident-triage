"""
Log ingestion and parsing module.
Supports flat log files and structured JSON logs.
"""
import re
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


SEVERITY_LEVELS = {"DEBUG": 0, "INFO": 1, "WARN": 2, "WARNING": 2, "ERROR": 3, "CRITICAL": 4}

LOG_PATTERN = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})\s+"
    r"(?P<level>DEBUG|INFO|WARN|WARNING|ERROR|CRITICAL)\s+"
    r"\[(?P<service>[^\]]+)\]\s+"
    r"(?P<message>.+)"
)


@dataclass
class LogEntry:
    timestamp: str
    level: str
    service: str
    message: str
    raw: str
    severity_score: int = field(init=False)

    def __post_init__(self):
        self.severity_score = SEVERITY_LEVELS.get(self.level.upper(), 0)


@dataclass
class ParsedLogBundle:
    entries: list[LogEntry]
    source: str
    parsed_at: str
    highest_severity: str
    affected_services: list[str]
    error_count: int
    critical_count: int

    def to_context_string(self) -> str:
        lines = [
            f"Log source: {self.source}",
            f"Total entries: {len(self.entries)} | Errors: {self.error_count} | Critical: {self.critical_count}",
            f"Affected services: {', '.join(self.affected_services)}",
            f"Highest severity: {self.highest_severity}",
            "",
            "--- LOG ENTRIES ---",
        ]
        for entry in self.entries:
            lines.append(f"[{entry.timestamp}] {entry.level} [{entry.service}] {entry.message}")
        return "\n".join(lines)


def parse_log_file(path: str | Path) -> ParsedLogBundle:
    path = Path(path)
    entries: list[LogEntry] = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            match = LOG_PATTERN.match(line)
            if match:
                entries.append(LogEntry(
                    timestamp=match.group("timestamp"),
                    level=match.group("level"),
                    service=match.group("service"),
                    message=match.group("message"),
                    raw=line,
                ))
    return _build_bundle(entries, source=path.name)


def parse_log_text(text: str, source: str = "pasted_log") -> ParsedLogBundle:
    entries: list[LogEntry] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        match = LOG_PATTERN.match(line)
        if match:
            entries.append(LogEntry(
                timestamp=match.group("timestamp"),
                level=match.group("level"),
                service=match.group("service"),
                message=match.group("message"),
                raw=line,
            ))
    return _build_bundle(entries, source=source)


def _build_bundle(entries: list[LogEntry], source: str) -> ParsedLogBundle:
    if not entries:
        return ParsedLogBundle(
            entries=[], source=source,
            parsed_at=datetime.now().isoformat(),
            highest_severity="NONE", affected_services=[],
            error_count=0, critical_count=0,
        )
    max_entry = max(entries, key=lambda e: e.severity_score)
    services = list(dict.fromkeys(e.service for e in entries))
    return ParsedLogBundle(
        entries=entries,
        source=source,
        parsed_at=datetime.now().isoformat(),
        highest_severity=max_entry.level,
        affected_services=services,
        error_count=sum(1 for e in entries if e.level in ("ERROR",)),
        critical_count=sum(1 for e in entries if e.level == "CRITICAL"),
    )