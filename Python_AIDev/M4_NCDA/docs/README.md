# Module 4: Numerical Computing and Data Analysis

- **LMS course:** [Modern Python & AI-Assisted Development](https://lms.snvaveranda.com/course/view.php?id=248)
- **Presentation URL/ID:** `https://lms.snvaveranda.com/mod/resource/view.php?id=8614` / `8614`

## Deck map

| Slides | Topic |
| --- | --- |
| 1–16 | Analysis workflow, NumPy, `ndarray`, and metadata |
| 17–41 | Creation, vectorized arithmetic, matrix products, ufuncs, and masks |
| 42–59 | Indexing, slicing, iteration, reshape, stacking, and splitting |
| 60–64 | NumPy file and image handling |
| 65–75 | pandas structures and input/output |
| 76–94 | Inspection, selection, mutation, filtering, and updating |
| 95–116 | Concatenation, joins, cleaning, missing values, and duplicates |
| 117–129 | Grouping, pivots, and aggregation |
| 130–133 | Summary and review |

## Learning objectives

Create and shape arrays; apply vectorized, aggregate, logical, and selection operations; load structured data; inspect, filter, combine, clean, group, and reshape pandas data for decision support.

> These notes summarize the protected deck for study; they do not reproduce its slide text, examples, or artwork.

## LMS demonstration walkthrough

- **Resources:** <https://lms.snvaveranda.com/mod/resource/view.php?id=8615> and <https://lms.snvaveranda.com/mod/resource/view.php?id=8616>.
- **Actual assignment:** 8615 covers NumPy array/matrix/file/image work and pandas structures, CSV/JSON I/O, selection, filtering, joins, missing data, and duplicates. Its practical records include student marks, employee-style fields, and `Car_sales.csv`. Resource 8616 is an in-class fundamentals notebook spanning input, types, conditionals, and collection review before analysis.
- **Input/data shape:** marks-style columns (`Sr. No.`, `College`, `Class`, `Exam_id`, `Name`, `Marks`); employee-style columns (`ID`, `Name`, `Age`, `Salary`, `Department`); and car columns for manufacturer/model, sales/resale, vehicle type, price/engine/power, dimensions, fuel, and launch date. Describe column types before loading.
- **Beginner workflow:** make a tiny synthetic frame, inspect shape/dtypes/nulls/duplicates, perform one vector operation, select/filter one rule, choose the join key and cardinality, validate row counts, then summarize. Add a downloaded CSV only after the synthetic case works.
- **Relationship to current examples:** `order_quality_analysis.py` is an **original extension beyond the LMS datasets**. It shares NumPy/pandas cleaning and joins but uses an independently defined order/warehouse contract.
- **Deliberate practice:** reproduce every result by hand for a two-row table; create one missing, duplicate, and unmatched key; predict each merge row count before execution; profile the result and record quarantine reasons.

See the detailed walkthrough at the end of `NOTES.md`; `examples/README.md` documents an optional local-download path.
