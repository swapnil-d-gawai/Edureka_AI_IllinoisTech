"""Framework-independent incident triage rules shared by the UI examples."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class Triage:
    """Immutable internal decision returned by the framework-independent rule."""

    severity: Literal["low", "medium", "high", "critical"]
    team: str
    rationale: str


def analyze_incident(subject: str, details: str) -> dict[str, str]:
    """Validate two text inputs and return a serializable deterministic routing result."""
    if len(subject.strip()) < 3 or len(details.strip()) < 10:
        raise ValueError("subject and details must meet minimum lengths")
    text = f"{subject} {details}".lower()
    if any(word in text for word in ("credential", "breach", "ransom")):
        triage = Triage("critical", "security", "Security indicator detected")
    elif any(word in text for word in ("outage", "all users", "unavailable")):
        triage = Triage("high", "service operations", "Broad service impact detected")
    elif any(word in text for word in ("slow", "degraded", "intermittent")):
        triage = Triage("medium", "application team", "Performance degradation detected")
    else:
        triage = Triage("low", "service desk", "No critical indicator detected")
    return {"severity": triage.severity, "team": triage.team, "rationale": triage.rationale}
