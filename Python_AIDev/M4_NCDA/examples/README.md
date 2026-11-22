# Order quality analysis

This NumPy/pandas exercise reconciles order transactions with warehouse stock. It parses numeric fields, removes invalid and duplicate orders, performs a cardinality-checked many-to-one join, computes vectorized values, evaluates inventory fulfillment, and produces regional aggregates.

```bash
python order_quality_analysis.py
python order_quality_analysis.py --orders orders.csv --warehouse warehouse.csv
```

Dependencies are `numpy` and `pandas`, commonly installed in the course environment. Outputs are `order_analysis.json` and `order_analysis.csv`. The default run intentionally includes one invalid row, one duplicate, and one SKU absent from stock.

Challenges: preserve a quarantine CSV with explicit reasons, verify warehouse SKU uniqueness, compute weighted shipping cost, and add an expected row-count assertion around the merge.
