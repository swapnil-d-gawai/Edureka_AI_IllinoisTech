"""Evaluate an AI-generated change proposal with deterministic quality gates."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import argparse
import ast
import json
import re
from typing import Callable


@dataclass(frozen=True)
class Change:
    """Proposal evidence consumed by deterministic review gates."""

    summary: str
    requirements: tuple[str, ...]
    patch: str
    test_patch: str
    validations: tuple[str, ...]


@dataclass(frozen=True)
class Finding:
    """One explainable rule result, including its severity and remediation signal."""

    rule: str
    severity: str
    message: str


@dataclass
class Gate:
    """Named, optionally disabled check composed from a callable."""

    name: str
    check: Callable[[Change], list[Finding]]
    enabled: bool = True
    findings: list[Finding] = field(default_factory=list)

    def run(self, change: Change) -> list[Finding]:
        """Execute this gate and retain findings for the final report."""
        self.findings = self.check(change) if self.enabled else []
        return self.findings


def syntax_gate(change: Change) -> list[Finding]:
    """Parse patch and test snippets to catch Python syntax defects."""
    findings: list[Finding] = []
    for label, code in (("patch", change.patch), ("tests", change.test_patch)):
        try:
            ast.parse(code)
        except SyntaxError as exc:
            findings.append(Finding("python-syntax", "error", f"{label}: {exc.msg} at line {exc.lineno}"))
    return findings


def secret_gate(change: Change) -> list[Finding]:
    """Flag a small set of likely credential literals without claiming a complete scan."""
    credential_names = {"api_key", "apikey", "api-key", "token", "password", "secret"}

    def is_secret_name(node: ast.expr) -> bool:
        """Return whether a Python identifier or mapping key names a credential."""
        return (
            isinstance(node, ast.Name) and node.id.lower() in credential_names
            or isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and node.value.lower() in credential_names
        )

    def is_secret_value(node: ast.expr) -> bool:
        """Require a literal value long enough to look like a credential."""
        return isinstance(node, ast.Constant) and isinstance(node.value, str) and len(node.value) >= 8

    for label, code in (("patch", change.patch), ("tests", change.test_patch)):
        try:
            tree = ast.parse(code)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Dict):
                if any(
                    key is not None and is_secret_name(key) and is_secret_value(value)
                    for key, value in zip(node.keys, node.values)
                ):
                    return [Finding("secret-scan", "error", "possible credential literal is present")]
            if isinstance(node, ast.Assign) and is_secret_value(node.value):
                if any(is_secret_name(target) for target in node.targets):
                    return [Finding("secret-scan", "error", "possible credential literal is present")]
            if isinstance(node, ast.AnnAssign) and node.value and is_secret_value(node.value):
                if is_secret_name(node.target):
                    return [Finding("secret-scan", "error", "possible credential literal is present")]
    return []


def unsafe_execution_gate(change: Change) -> list[Finding]:
    """Identify risky constructs that need an explicit human security review."""
    blocked: set[str] = set()
    for code in (change.patch, change.test_patch):
        try:
            tree = ast.parse(code)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec"}:
                    blocked.add(f"{node.func.id}(")
                for keyword in node.keywords:
                    if (
                        keyword.arg == "shell"
                        and isinstance(keyword.value, ast.Constant)
                        and keyword.value.value is True
                    ):
                        blocked.add("shell=True")
                    if (
                        keyword.arg == "verify"
                        and isinstance(keyword.value, ast.Constant)
                        and keyword.value.value is False
                    ):
                        blocked.add("verify=False")
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                value = node.value
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                if isinstance(value, ast.Constant) and value.value is True:
                    if any(isinstance(target, ast.Name) and target.id == "shell" for target in targets):
                        blocked.add("shell=True")
                if isinstance(value, ast.Constant) and value.value is False:
                    if any(isinstance(target, ast.Name) and target.id == "verify" for target in targets):
                        blocked.add("verify=False")
    return [
        Finding("unsafe-pattern", "error", f"risky construct requires review: {name}")
        for name in sorted(blocked)
    ]


def requirement_gate(change: Change) -> list[Finding]:
    """Use visible keywords as a heuristic for requirement-evidence gaps."""
    if not change.requirements:
        return [Finding("requirements", "error", "no acceptance requirements were supplied")]
    missing: list[str] = []
    lowered = f"{change.summary}\n{change.test_patch}".lower()
    for requirement in change.requirements:
        keywords = [word for word in re.findall(r"[a-zA-Z][a-zA-Z-]{3,}", requirement.lower()) if word not in {"when", "then", "must"}]
        if keywords and not any(keyword in lowered for keyword in keywords[:3]):
            missing.append(requirement)
    return [Finding("requirements", "warning", f"no visible test or summary evidence for: {item}") for item in missing]


def test_gate(change: Change) -> list[Finding]:
    """Require the minimum recognizable pytest test and assertion structure."""
    try:
        tree = ast.parse(change.test_patch)
    except SyntaxError:
        return []
    test_functions = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")
    ]
    if not test_functions:
        return [Finding("tests", "error", "test change contains no pytest test function")]
    has_check = any(
        isinstance(node, ast.Assert)
        or isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "raises"
        for function in test_functions
        for node in ast.walk(function)
    )
    if not has_check:
        return [Finding("tests", "error", "test change contains no assertion")]
    return []


def validation_gate(change: Change) -> list[Finding]:
    """Check that an independent validation command was actually recorded."""
    return (
        [Finding("validation", "warning", "no command was recorded for independent validation")]
        if not change.validations
        else []
    )


def sample_change() -> Change:
    """Return a clean proposal that demonstrates a review-without-errors result."""
    return Change(
        summary="Add a normalized customer identifier validator",
        requirements=("Reject blank identifiers", "Normalize identifier whitespace"),
        patch=(
            "def normalize_customer_id(value: str) -> str:\n"
            "    if not isinstance(value, str):\n"
            "        raise TypeError('value must be a string')\n"
            "    normalized = value.strip().upper()\n"
            "    if not normalized:\n"
            "        raise ValueError('customer id is required')\n"
            "    return normalized\n"
        ),
        test_patch=(
            "def test_normalize_customer_id():\n"
            "    assert normalize_customer_id('  ab-12 ') == 'AB-12'\n\n"
            "def test_blank_identifier():\n"
            "    import pytest\n"
            "    with pytest.raises(ValueError):\n"
            "        normalize_customer_id('   ')\n"
        ),
        validations=("python -m pytest -q",),
    )


def evaluate(change: Change) -> dict[str, object]:
    """Run the complete deterministic gate set and summarize the decision."""
    gates = [
        Gate("syntax", syntax_gate),
        Gate("secrets", secret_gate),
        Gate("unsafe", unsafe_execution_gate),
        Gate("requirements", requirement_gate),
        Gate("tests", test_gate),
        Gate("validation-record", validation_gate),
    ]
    findings = [finding for gate in gates for finding in gate.run(change)]
    errors = sum(item.severity == "error" for item in findings)
    return {
        "summary": change.summary,
        "decision": "block" if errors else "review",
        "errors": errors,
        "warnings": sum(item.severity == "warning" for item in findings),
        "findings": [item.__dict__ for item in findings],
        "gates": [gate.name for gate in gates],
    }


def main() -> int:
    """Load proposal evidence, write the report, and return block/success status."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="JSON object matching the Change fields")
    parser.add_argument("--output", type=Path, default=Path("change_gate_report.json"))
    args = parser.parse_args()
    try:
        if args.input:
            data = json.loads(args.input.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("input JSON must contain an object")
            for key in ("requirements", "validations"):
                if isinstance(data.get(key), list):
                    data[key] = tuple(data[key])
            change = Change(**data)
        else:
            change = sample_change()
        report = evaluate(change)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 1 if report["decision"] == "block" else 0
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(f"error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
