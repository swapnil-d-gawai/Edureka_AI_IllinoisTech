# Service reliability dashboard

`ops_dashboard.py` creates an operations review with a latency trend and SLA, service error-rate comparison, regional distribution, and volume/availability relationship. It uses deterministic synthetic data, validates external CSV inputs, and always saves headlessly through Matplotlib's `Agg` backend.

```bash
python ops_dashboard.py
python ops_dashboard.py --input operations.csv --latency-sla 220 --output report.png
```

Expected output is `service_reliability_dashboard.png` plus a JSON summary. Required CSV columns are listed in `load_data()`. The default data is generated locally; no dataset download or display server is required.

Challenges: add a chart choice from the deck, annotate the 95th-percentile latency, compare regions with shared scales, add a colorblind-safe export profile, and write a visual-regression smoke test.

## LMS bridge and local dataset path

LMS resources 8618/8619 use `Car_sales.csv` for Matplotlib charting and customization; resource 8620 uses `top50.csv` for subplots and `GridSpec`. `ops_dashboard.py` is an original operations-domain extension and does not use those files.

To follow a downloaded dataset locally, keep it outside tracked source:

```text
local_lms_data/
  Car_sales.csv
  top50.csv
```

For a quick bridge, load one file with `pd.read_csv`, select three columns, create one labeled axes, and compare its numeric summary before making a subplot. The optional path is for local study only; do not commit LMS archives, PDFs, notebooks, or CSVs. Keep the default example invocation for deterministic offline behavior.
