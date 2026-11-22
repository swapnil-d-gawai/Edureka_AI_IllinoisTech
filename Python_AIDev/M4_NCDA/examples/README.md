# Order quality analysis

This NumPy/pandas exercise reconciles order transactions with warehouse stock. It parses numeric fields, removes invalid and duplicate orders, performs a cardinality-checked many-to-one join, computes vectorized values, evaluates inventory fulfillment, and produces regional aggregates.

```bash
python order_quality_analysis.py
python order_quality_analysis.py --orders orders.csv --warehouse warehouse.csv
```

Dependencies are `numpy` and `pandas`, commonly installed in the course environment. Outputs are `order_analysis.json` and `order_analysis.csv`. The default run intentionally includes one invalid row, one duplicate, and one SKU absent from stock.

Challenges: preserve a quarantine CSV with explicit reasons, verify warehouse SKU uniqueness, compute weighted shipping cost, and add an expected row-count assertion around the merge.

## LMS bridge

LMS resource 8615 demonstrates NumPy plus pandas inspection, filtering, joins, missing values, and duplicates across marks, employee-style, and car data; resource 8616 is a fundamentals practical. This order/warehouse example is an original extension with a different schema.

The default stays offline. To bring your own downloaded LMS-like CSV, create an ignored local directory outside tracked examples and adapt the columns first; for example:

```text
local_lms_data/
  marks.csv
  sample_data.csv
  Car_sales.csv
```

Run `pd.read_csv("local_lms_data/Car_sales.csv")` in a throwaway analysis script, print `shape`, `dtypes`, nulls, and duplicates, and only then recreate one LMS analysis with synthetic names/values. Do not feed `Car_sales.csv` directly to `order_quality_analysis.py`: its manufacturer/model schema is not the required `order_id`, `sku`, `quantity`, and `unit_price` contract. Never commit the downloaded files.
