"""Validate model JSON and dispatch only allowlisted read-only tools.

The model produces proposals; parsing, validation, routing, and authorization remain
ordinary application responsibilities.
"""

from dataclasses import dataclass
from json import JSONDecodeError, loads
from typing import Any, Callable, Protocol

SEVERITIES = ("low", "medium", "high", "critical")


class ValidationError(ValueError):
    pass


@dataclass(frozen=True)
class ToolRequest:
    # Dataclass construction is a useful typed representation, but its shallow check
    # must be followed by tool-specific argument validation in the tool function.
    tool: str
    arguments: dict[str, Any]

    def __post_init__(self) -> None:
        if not self.tool.strip() or not isinstance(self.arguments, dict):
            raise ValidationError("tool and arguments must be valid")


@dataclass(frozen=True)
class IncidentPlan:
    incident_id: str
    severity: str
    summary: str
    needs_human_review: bool
    tool_request: ToolRequest


class RawModel(Protocol):
    # Protocol is the replaceable raw-text provider boundary; it intentionally does
    # not make the model responsible for validation or tool execution.
    def generate(self, prompt: str) -> str: ...


class MockRawModel:
    def __init__(self) -> None:
        self.calls = 0

    def generate(self, prompt: str) -> str:
        self.calls += 1
        if self.calls == 1:
            return '{"incident_id": "INC-7", "severity": "high"}'
        return (
            '{"incident_id":"INC-7","severity":"high",'
            '"summary":"Checkout latency is above the agreed threshold.",'
            '"needs_human_review":true,'
            '"tool_request":{"tool":"get_metrics",'
            '"arguments":{"service":"checkout","minutes":15}}}'
        )


def require_string(value: Any, field: str, max_length: int) -> str:
    if not isinstance(value, str) or not 1 <= len(value.strip()) <= max_length:
        raise ValidationError(f"{field} must be a non-empty string of at most {max_length}")
    return value.strip()


def validate_plan(raw: str) -> IncidentPlan:
    # The validator distinguishes malformed JSON, wrong top-level type, exact-field
    # shape, enum/type errors, and the nested tool contract.
    try:
        value = loads(raw)
    except JSONDecodeError as error:
        raise ValidationError(f"malformed JSON: {error.msg}") from error
    if not isinstance(value, dict):
        raise ValidationError("top-level value must be an object")
    required = {
        "incident_id",
        "severity",
        "summary",
        "needs_human_review",
        "tool_request",
    }
    if set(value) != required:
        raise ValidationError(f"fields must be exactly {sorted(required)}")
    severity = value["severity"]
    if severity not in SEVERITIES:
        raise ValidationError("severity is not allowlisted")
    review = value["needs_human_review"]
    if not isinstance(review, bool):
        raise ValidationError("needs_human_review must be boolean")
    tool_value = value["tool_request"]
    if not isinstance(tool_value, dict) or set(tool_value) != {"tool", "arguments"}:
        raise ValidationError("tool_request contract is invalid")
    tool = ToolRequest(
        require_string(tool_value["tool"], "tool", 60),
        tool_value["arguments"],
    )
    return IncidentPlan(
        require_string(value["incident_id"], "incident_id", 40),
        severity,
        require_string(value["summary"], "summary", 500),
        review,
        tool,
    )


def get_metrics(arguments: dict[str, Any]) -> dict[str, Any]:
    # bool is an int subclass in Python, so it is explicitly rejected for minutes.
    if set(arguments) != {"service", "minutes"}:
        raise ValidationError("get_metrics requires service and minutes only")
    service = require_string(arguments["service"], "service", 40)
    minutes = arguments["minutes"]
    if isinstance(minutes, bool) or not isinstance(minutes, int) or not 1 <= minutes <= 60:
        raise ValidationError("minutes must be an integer from 1 through 60")
    return {"service": service, "minutes": minutes, "p95_latency_ms": 920}


TOOLS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    # A fixed in-code allowlist keeps the model from selecting dynamic shell/SQL/URL
    # functions. Adding a tool is an application permission change.
    "get_metrics": get_metrics
}


def dispatch(request: ToolRequest) -> dict[str, Any]:
    function = TOOLS.get(request.tool)
    if function is None:
        raise PermissionError(f"tool {request.tool!r} is not allowlisted")
    return function(request.arguments)


def request_plan(model: RawModel, prompt: str, max_attempts: int = 2) -> IncidentPlan:
    if not 1 <= max_attempts <= 3:
        raise ValueError("max_attempts must be between 1 and 3")
    last_error: ValidationError | None = None
    for _ in range(max_attempts):
        try:
            return validate_plan(model.generate(prompt))
        except ValidationError as error:
            # Feedback can repair syntax/schema once, but the bounded loop cannot silently
            # invent missing business facts.
            last_error = error
            prompt += f"\nValidation feedback: {error}. Correct the structure."
    assert last_error is not None
    raise last_error


def main() -> None:
    # The first mock response is intentionally incomplete; the second is valid.
    model = MockRawModel()
    plan = request_plan(model, "Produce an incident plan and request approved read-only metrics.")
    print(plan)
    print("Tool result:", dispatch(plan.tool_request))
    try:
        dispatch(ToolRequest("run_shell", {"command": "delete records"}))
    except PermissionError as error:
        print("Unsafe request blocked:", error)


if __name__ == "__main__":
    main()
