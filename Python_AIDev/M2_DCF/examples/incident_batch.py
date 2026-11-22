"""Validate, classify, and summarize a JSONL incident batch."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import argparse
import json


SEVERITIES = {"low", "medium", "high", "critical"}


def classify(record: dict[str, object]) -> tuple[str, str]:
    """Route one validated tagged-event mapping to a queue and audit detail."""
    match record:
        case {"kind": "service", "severity": severity, "region": region}:
            if not isinstance(severity, str) or severity not in SEVERITIES or not isinstance(region, str):
                raise ValueError("invalid service incident")
            return ("page-on-call" if severity in {"high", "critical"} else "normal-queue", str(region))
        case {"kind": "security", "severity": severity, "indicator_count": count}:
            if (
                not isinstance(severity, str)
                or severity not in SEVERITIES
                or isinstance(count, bool)
                or not isinstance(count, int)
                or count < 1
            ):
                raise ValueError("invalid security incident")
            return ("security-team", f"indicators:{count}")
        case {"kind": "data", "severity": severity, "rows_affected": rows}:
            if (
                not isinstance(severity, str)
                or severity not in SEVERITIES
                or isinstance(rows, bool)
                or not isinstance(rows, int)
                or rows < 0
            ):
                raise ValueError("invalid data incident")
            return ("data-platform", f"rows:{rows}")
        case _:
            raise ValueError("unknown or incomplete incident shape")


def process_lines(path: Path) -> dict[str, object]:
    """Validate JSONL rows, preserve rejects, and deduplicate accepted incident IDs."""
    if not path.is_file():
        raise FileNotFoundError(path)
    accepted: list[dict[str, object]] = []
    rejected: list[dict[str, object]] = []
    # Streaming one line at a time avoids loading the whole batch into memory.
    with path.open("r", encoding="utf-8") as stream:
        for line_number, raw_line in enumerate(stream, start=1):
            if not raw_line.strip():
                rejected.append({"line": line_number, "reason": "blank line"})
                continue
            try:
                record = json.loads(raw_line)
                if not isinstance(record, dict):
                    raise ValueError("record must be an object")
                incident_id = record.get("id")
                if not isinstance(incident_id, str) or not incident_id.strip():
                    raise ValueError("id must be non-empty")
                queue, detail = classify(record)
                accepted.append({**record, "queue": queue, "detail": detail})
            except (json.JSONDecodeError, ValueError) as exc:
                rejected.append({"line": line_number, "reason": str(exc), "raw": raw_line[:120].rstrip()})

    # The two-stage design keeps validation errors tied to lines before applying the ID policy.
    seen: set[str] = set()
    unique: list[dict[str, object]] = []
    for record in accepted:
        incident_id = str(record["id"])
        if incident_id in seen:
            rejected.append({"line": None, "reason": f"duplicate id {incident_id}"})
        else:
            seen.add(incident_id)
            unique.append(record)
    return {
        "source": str(path),
        "accepted": unique,
        "rejected": rejected,
        "metrics": {
            "accepted_count": len(unique),
            "rejected_count": len(rejected),
            "queue_counts": dict(Counter(str(row["queue"]) for row in unique)),
        },
    }


def write_report(report: dict[str, object], output: Path) -> None:
    """Write beside the destination, then replace it to avoid publishing partial JSON."""
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".pending")
    temporary.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    temporary.replace(output)


def create_sample(path: Path) -> None:
    """Create input covering valid, invalid, blank, and duplicate records."""
    rows = [
        '{"id":"INC-100","kind":"service","severity":"critical","region":"eu"}',
        '{"id":"SEC-4","kind":"security","severity":"high","indicator_count":3}',
        '{"id":"BAD","kind":"data","severity":"low","rows_affected":-1}',
        "",
        '{"id":"INC-100","kind":"service","severity":"low","region":"us"}',
    ]
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def main() -> int:
    """Run the batch and distinguish clean, reject-bearing, and fatal exit statuses."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", type=Path)
    parser.add_argument("--output", type=Path, default=Path("incident_report.json"))
    args = parser.parse_args()
    generated = args.input is None
    path = args.input or Path("sample_incidents.jsonl")
    try:
        if generated:
            create_sample(path)
        report = process_lines(path)
        write_report(report, args.output)
        print(json.dumps(report["metrics"], indent=2))
        return 0 if not report["rejected"] else 1
    except (OSError, ValueError) as exc:
        print(f"error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
