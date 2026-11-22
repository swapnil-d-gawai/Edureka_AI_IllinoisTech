# Module 4 Notes: Numerical Computing and Data Analysis

This module aligns to the LMS topics for NumPy arrays, vectorization, selection/shaping, pandas input/output and inspection, filtering, joining, cleaning, grouping, and pivoting. The core data-engineering habit is to keep raw input immutable and make every cleaning rule observable.

## 1. Choose the level of tool

| Need | Python building block |
| --- | --- |
| A small ordered collection | list/tuple |
| One-dimensional labeled data | pandas `Series` |
| Relational/table-like transformation | pandas `DataFrame` |
| Dense numeric arrays or matrix operations | NumPy `ndarray` |
| Durable, SQL-governed joins at scale | database |

Pandas is convenient in the space occupied by spreadsheet analysis and moderate ETL. SQL is often still better for joins and transformations close to a database. A competent pipeline can use SQL for governed extraction, pandas for local feature/quality checks, and files for handoff.

## 2. NumPy arrays

An **array** stores values with a shape and one common dtype.

```python
values = np.array([10, 20, 30], dtype=np.int64)
print(values.shape)  # (3,)
print(values.dtype)  # int64
```

Important metadata:

- `shape`: size along each axis,
- `ndim`: number of axes,
- `dtype`: storage type,
- `strides`: byte steps in memory,
- `size`: total element count.

A list can contain mixed types. An array is optimized for homogeneity, which is why adding `"four"` into a numeric array behaves differently from adding it to a Python list.

## 3. Vectorization

Vectorization applies an operation across an array without an explicit Python loop:

```python
quantity = np.array([2, 3, 5])
price = np.array([10.0, 4.0, 2.5])
gross = quantity * price
```

Output:

```text
[20.  12.  12.5]
```

The operation runs element by element. `@` or `np.dot()` is matrix multiplication, not `*`.

```python
left = np.array([[1, 2]])
right = np.array([[3], [4]])
print(left @ right)  # [[11]]
```

Why “compiled code” does not mean every vectorized pipeline is always fastest: small arrays, copies, and poor layouts can dominate. Benchmark realistic data.

## 4. Broadcasting

Broadcasting aligns dimensions from right to left.

```python
matrix = np.array([[1, 2], [3, 4]])
weights = np.array([10, 100])
print(matrix * weights)
```

Output:

```text
[[ 10 200]
 [ 30 400]]
```

`weights` is broadcast across each row. If dimensions cannot be aligned (except where one dimension is `1`), NumPy raises an error. Do not rely on broadcasting when business dimensions are ambiguous; reshape or explicitly validate.

## 5. Masks, indexing, and views

A Boolean mask retains matching positions:

```python
orders = np.array([2, -1, 4])
valid = orders > 0
print(valid)          # [ True False  True]
print(orders[valid])  # [2 4]
```

Indexing styles:

- basic integer/slice: addresses a position/range,
- Boolean mask: selects based on truth values,
- fancy indexing with integer arrays: builds a new selection,
- `np.where(condition, if_true, if_false)`: element-wise choice.

A basic slice is commonly a **view**:

```python
source = np.array([1, 2, 3])
subset = source[:2]
subset[0] = 99
print(source)  # [99 2 3]
```

When a downstream stage must own independent values, use `.copy()`.

## 6. Reshaping and combining

`reshape` changes shape metadata but preserves a traversal order:

```python
np.arange(6).reshape(2, 3)
```

produces:

```text
[[0 1 2]
 [3 4 5]]
```

`np.stack` creates a new axis; `np.concatenate` joins along an existing one. State expected axis and resulting shape before writing either.

## 7. pandas: the labeled table

A `Series` is one-dimensional and index-labeled:

```python
amounts = pd.Series([10.0, 5.0], index=["A", "B"])
```

A `DataFrame` is two-dimensional and allows different dtypes by column. It is table-like, but row and column labels plus in-memory indexing make pandas richer than a plain CSV.

Inspect before transforming:

```python
frame.head()
frame.info()
frame.dtypes
frame.isna().sum()
frame.duplicated("order_id").sum()
```

These checks are analogous to source profiling in an ETL mapping.

## 8. Selection, filtering, and updates

Column selection: `frame["quantity"]`.

Row selection with labels: `.loc`.

```python
east = frame.loc[frame["region"].eq("east"), ["order_id", "quantity"]]
```

Why `.loc`? It separates intent from the integer-address `.iloc` model.

Avoid chained assignment:

```python
frame[frame["quantity"] < 0]["quantity"] = 0  # ambiguous ownership
```

Use a single label-based assignment on the intended copy:

```python
mask = frame["quantity"].lt(0)
frame.loc[mask, "quantity"] = 0
```

Do not silently fix a negative order quantity without a business rule. A reject path is often safer.

## 9. Explicit parsing

CSV infers types, but inference is not validation:

```python
numeric = frame.assign(
    quantity=pd.to_numeric(frame["quantity"], errors="coerce")
)
```

`errors="coerce"` turns invalid values into missing values. Record and quarantine that outcome. If the schema requires all values to be valid, a blind coercion can hide source corruption.

For dates:

```python
pd.to_datetime(frame["event_date"], errors="coerce", utc=True)
```

Preserve the original column until checks pass.

## 10. Cleaning policy

Cleaning must answer:

1. Which values are missing?
2. Is missingness business-meaningful?
3. Should records be rejected, retained, or imputed?
4. Is a duplicate exact, or is the first row a policy choice?
5. Can the original raw data be reproduced?

Common tools:

```python
frame.dropna()
frame.fillna(...)
frame.replace(...)
frame.drop_duplicates("order_id", keep="first")
```

Mean imputation for a missing delivery duration may change operating metrics. Imputing with a business-approved default, preserving an indicator flag, or rejecting may be more defensible.

## 11. SQL-like joins

```python
enriched = orders.merge(
    warehouse,
    on="sku",
    how="left",
    validate="many_to_one",
    indicator=True,
)
```

`how="left"` keeps every valid order. `validate="many_to_one"` fails when the warehouse side has repeated SKU values and would multiply order rows. This is comparable to declaring and testing relational cardinality, but the actual key quality still needs inspection.

`indicator=True` adds `_merge` categories:

- `both`: key matched,
- `left_only`: order has no warehouse match,
- `right_only`: unused warehouse key (more useful for outer/right joins).

## 12. Grouping and pivoting

Group-by is SQL-like `GROUP BY`:

```python
summary = orders.groupby("region").agg(
    order_count=("order_id", "nunique"),
    gross_value=("gross_value", "sum"),
)
```

A pivot table reshapes categories into columns or rows for cross-tab reporting. Specify `aggfunc` and missing behavior. Aggregating before validating row counts can produce a confident-looking but incorrect KPI.

## 13. Order-analysis walkthrough

Sample inputs conceptually contain:

- six order rows,
- one negative quantity,
- one duplicate order ID,
- one SKU absent from warehouse.

The example:

1. Converts quantity and price numerically.
2. Defines completeness and business-validity masks.
3. Keeps a copy of valid rows.
4. Reports invalid and duplicate counts.
5. Performs cardinality-checked `many_to_one` merge.
6. Computes vectorized gross value and fulfillment.
7. Summarizes by region.
8. Writes JSON metrics and CSV enriched rows.

Expected default metrics:

```text
input_rows: 6
invalid_rows: 1
duplicate_rows: 1
unmatched_skus: 1
```

The remaining valid unique order rows depend on the sample definition shown in `sample_data()`.

## 14. Debugging pandas and NumPy

1. Print `shape`, `columns`, `dtypes`, and null counts at each pipeline boundary.
2. Reduce to one row and evaluate the mask separately.
3. Check index alignment; arithmetic between labeled objects aligns labels, not just positions.
4. Before/after a join, compare expected cardinality.
5. Inspect unique key values; whitespace and casing cause silent unmatched rows.
6. For warnings, locate chained assignment and ambiguous truth values.
7. Use `repr` for small Series values to reveal hidden dtypes.
8. Ensure generated output directories exist.

## 15. Common mistakes

- Using `*` for matrix multiplication.
- Assuming a displayed number's precision equals its stored representation.
- Treating `.isna()` as a scalar in an `if`.
- Joining on a nonunique reference key.
- Dropping rejects before reporting them.
- Imputing with no rationale.
- Confusing a view with an independent copy.
- Resetting index and accidentally retaining duplicate labels.

## 16. Practice

1. Construct a 2×3 array, multiply it by a length-3 weight vector, and calculate its shape.
2. Demonstrate a slice changing the original array, then solve it with `.copy()`.
3. Load two CSVs, profile missing and duplicate values, and state expected row counts.
4. Implement a left join with `validate`.
5. Compute a region KPI and compare it to a hand-calculated two-row case.
6. Preserve a quarantine frame with an explicit reason code for each rejection.
7. Write tests for duplicate warehouse SKU, invalid price, missing column, and empty input.

## 17. LMS demonstration walkthrough

**Exact resources:** [demonstration 8615](https://lms.snvaveranda.com/mod/resource/view.php?id=8615) and [in-class practical 8616](https://lms.snvaveranda.com/mod/resource/view.php?id=8616).

### Actual scenario and data

The main archive builds from array/matrix arithmetic, ufuncs/aggregation, NumPy text/binary/image handling, pandas Series/DataFrame construction and CSV I/O, selection/filtering, then concatenation, left/right/inner/outer/self joins, missing values, and duplicates. It uses marks, employee-style sample records, and a car-sales table. The separate in-class notebook revisits Python fundamentals needed before analysis.

The LMS-like schemas, expressed as field contracts rather than copied records, are:

- marks: `Sr. No.`, `College`, `Class`, `Exam_id`, `Name`, `Marks`;
- employees: `ID`, `Name`, `Age`, `Salary`, `Department`;
- cars: `Manufacturer`, `Model`, `Sales in thousands`, `4-year resale value`, `Vehicle type`, `Price in thousands`, `Engine size`, `Horsepower`, physical dimensions/weight, fuel/capacity/efficiency, and `Latest Launch`.

A synthetic practice row can be:

```text
ID,Name,Age,Salary,Department
101,Example A,31,62000,Support
```

Do not commit the downloaded `marks.csv`, `sample_data.csv`, `Car_sales.csv`, or extracted notebooks.

### Step-by-step beginner workflow

1. Start with a two-row synthetic DataFrame whose expected values you can calculate.
2. Print `shape`, columns, dtypes, missing counts, and duplicate count before changing anything.
3. Create a NumPy array from one numeric column and demonstrate broadcasting with a clearly shaped weight.
4. Convert numeric/date text explicitly; preserve invalid values in a reject record.
5. Filter one business rule and inspect the Boolean mask itself.
6. Build two tiny frames with one shared and one unmatched key.
7. State expected result counts, execute one join at a time, and use merge validation/indicator to verify many-to-one behavior.
8. Add one missing value and one duplicate; decide whether to reject, fill, or retain and record why.
9. Aggregate by one category and compare the output with a hand calculation.
10. Only then replace synthetic data with a CSV downloaded from the LMS.

### Connection to the current examples

The default `order_quality_analysis.py` is an **original extension beyond the LMS demonstrations**. It shares the analysis toolkit but introduces a different order/warehouse schema, explicit quality masks, duplicate policy, a cardinality-checked join, and JSON/CSV outputs. The repository intentionally does not include the LMS datasets.

### Deliberate practice

For each table, create four records: clean, missing, duplicate, and wrong type. Predict expected kept/rejected/joined counts before loading. Ask whether a value of zero, an empty string, and `NaN` represent the same business state. Write down the join key and allowed cardinality. Finish with a group aggregate and verify it against a two-row hand calculation.
