"""Runnable FastAPI service for validated support-triage requests."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
import os
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field


class Severity(str, Enum):
    """Public severity values accepted and returned by the API."""

    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class TicketCreate(BaseModel):
    """Validated client input; these bounds become part of the OpenAPI contract."""

    subject: str = Field(min_length=3, max_length=160)
    body: str = Field(min_length=10, max_length=10_000)
    service: str = Field(min_length=2, max_length=80)


class TriageResult(BaseModel):
    """Stable public output, intentionally separate from the request shape."""

    id: str
    service: str
    severity: Severity
    route: str
    summary: str
    provider: str
    created_at: datetime


class Classifier:
    """Classifier boundary that route code can replace without changing HTTP contracts."""

    async def classify(self, ticket: TicketCreate) -> tuple[Severity, str, str]:
        """Apply deterministic local rules without network calls or mutable state."""
        text = f"{ticket.subject} {ticket.body}".lower()
        if any(token in text for token in ("breach", "security", "ransom")):
            return Severity.critical, "security-operations", text[:100]
        if any(token in text for token in ("outage", "unavailable", "all users")):
            return Severity.high, "service-desk-l2", text[:100]
        if "slow" in text or "degraded" in text:
            return Severity.medium, "service-desk-l1", text[:100]
        return Severity.low, "general-support", text[:100]


class OptionalExternalClassifier(Classifier):
    """Placeholder showing where an environment-configured provider belongs."""

    async def classify(self, ticket: TicketCreate) -> tuple[Severity, str, str]:
        """Fall back locally unless an external integration is explicitly configured."""
        # Integrations are deliberately not imported or called in this example.
        if not os.getenv("TRIAGE_PROVIDER_ENDPOINT"):
            return await super().classify(ticket)
        raise RuntimeError("external provider adapter is intentionally not implemented")


class TicketStore:
    """Minimal process-local storage used to demonstrate a replaceable persistence boundary."""

    def __init__(self) -> None:
        """Start an empty store; production replacements would own persistence."""
        self._items: dict[str, TriageResult] = {}

    def save(self, item: TriageResult) -> TriageResult:
        """Store and return a result so route behavior remains easy to follow."""
        self._items[item.id] = item
        return item

    def get(self, item_id: str) -> TriageResult | None:
        """Return one ticket or ``None`` when the process does not know the ID."""
        return self._items.get(item_id)

    def list(self, severity: Severity | None = None) -> list[TriageResult]:
        """Return a detached list, optionally filtered by the public severity type."""
        values = list(self._items.values())
        return [item for item in values if severity is None or item.severity == severity]


store = TicketStore()
app = FastAPI(title="Support Triage API", version="1.0.0")


def classifier_dependency() -> Classifier:
    """Construct the classifier behind FastAPI's replaceable dependency mechanism."""
    return OptionalExternalClassifier()


@app.get("/health")
async def health() -> dict[str, str]:
    """Report whether the configured classifier mode can actually serve requests."""
    return {"status": "healthy", "mode": "mock" if not os.getenv("TRIAGE_PROVIDER_ENDPOINT") else "unavailable-provider"}


@app.post("/tickets", response_model=TriageResult, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket: TicketCreate,
    classifier: Annotated[Classifier, Depends(classifier_dependency)],
) -> TriageResult:
    """Validate a ticket, classify it, and persist the 201 response representation."""
    try:
        severity, route, summary = await classifier.classify(ticket)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    result = TriageResult(
        id=uuid4().hex,
        service=ticket.service.strip(),
        severity=severity,
        route=route,
        summary=summary,
        provider="local-rules",
        created_at=datetime.now(timezone.utc),
    )
    return store.save(result)


@app.get("/tickets", response_model=list[TriageResult])
async def list_tickets(severity: Annotated[Severity | None, Query()] = None) -> list[TriageResult]:
    """List process-local triage results with an optional validated filter."""
    return store.list(severity)


@app.get("/tickets/{ticket_id}", response_model=TriageResult)
async def get_ticket(ticket_id: str) -> TriageResult:
    """Retrieve a process-local result or return the standard resource-missing status."""
    item = store.get(ticket_id)
    if item is None:
        raise HTTPException(status_code=404, detail="ticket not found")
    return item


@app.get("/tickets/{ticket_id}/stream")
async def stream_ticket_summary(ticket_id: str) -> StreamingResponse:
    """Stream a stored summary using blank-line-terminated Server-Sent Events."""
    item = store.get(ticket_id)
    if item is None:
        raise HTTPException(status_code=404, detail="ticket not found")

    async def events():
        """Produce the summary token stream plus a completion event."""
        # Yield small independent events so clients can render progress before completion.
        for word in item.summary.split():
            yield f"data: {word}\n\n"
        yield "event: complete\ndata: done\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")


# Run: uvicorn support_triage_api:app --reload
