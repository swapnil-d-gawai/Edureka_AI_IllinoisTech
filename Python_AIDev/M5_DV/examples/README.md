# Service reliability dashboard

`ops_dashboard.py` creates an operations review with a latency trend and SLA, service error-rate comparison, regional distribution, and volume/availability relationship. It uses deterministic synthetic data, validates external CSV inputs, and always saves headlessly through Matplotlib's `Agg` backend.

```bash
python ops_dashboard.py
python ops_dashboard.py --input operations.csv --latency-sla 220 --output report.png
```

Expected output is `service_reliability_dashboard.png` plus a JSON summary. Required CSV columns are listed in `load_data()`. The default data is generated locally; no dataset download or display server is required.

Challenges: add a chart choice from the deck, annotate the 95th-percentile latency, compare regions with shared scales, add a colorblind-safe export profile, and write a visual-regression smoke test.
