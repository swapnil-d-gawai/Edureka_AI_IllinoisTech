# Incident batch processor

`incident_batch.py` reads JSON Lines, pattern-matches tagged event shapes, validates fields, detects duplicate IDs, quarantines bad records, and writes a report through an adjacent pending file. With no arguments it creates `sample_incidents.jsonl`.

```bash
python incident_batch.py
python incident_batch.py my_incidents.jsonl --output reports/triage.json
```

Expected exit code is 1 when valid work contains rejected rows, 0 for a clean batch, and 2 for an input/output-level failure. Inspect `incident_report.json` for accepted records, reasons, and queue counts.

Challenges: add `match` cases for maintenance and customer events, process a `.csv` input with `csv.DictReader`, reject unknown keys, and write a separate rejected-only file with stable ordering.

## LMS bridge

First use LMS resource 8611 to isolate one example for conditionals/loops, files, and each collection. Resource 15705's extracted scripts are an introductory review; they are not the incident schema used here. `incident_batch.py` is an original integration exercise: after the isolated notebook behavior works, compare its synthetic JSON Lines contract with the walkthrough in `docs/NOTES.md`. No downloaded dataset is required.
