# Module 1 Notes: Python Programming Essentials

These notes align with the Module 1 LMS deck map: Python and generative AI, the execution model, variables and syntax, output formatting, built-in data types, and operators. The examples are original study explanations rather than reproductions of the protected slides.

## 1. Start with the problem, not the language

A **program** is a repeatable set of instructions. A useful first comparison is a Unix or AutoSys job:

| Existing experience | Python equivalent |
| --- | --- |
| SQL query or Informatica mapping | Transformation logic |
| ETL job parameters | Function arguments or a configuration dictionary |
| AutoSys/TWS job definition | Python program launched by a scheduler |
| Shell script exit code | A Python process exit code such as `0`, `1`, or `2` |
| SQL `NULL` | Python `None` (usually) |

Python often coordinates work rather than replacing every specialized tool. It can read a file, validate each record, call an AI model, write a report, and return an exit code that a scheduler can understand.

**Mental model:** Python is the executable form of a runbook. Data is the work order, control flow is the routing rule, and functions are named reusable job steps.

### A first complete program

```python
job_name = "daily_customer_load"
row_count = 1250
failed = False

if failed:
    print(f"{job_name}: FAILED")
else:
    print(f"{job_name}: loaded {row_count} rows")
```

Input/state: `failed` is `False`.

Output:

```text
daily_customer_load: loaded 1250 rows
```

Line-by-line reasoning:

1. Names are assigned values; Python infers each value's type.
2. The `if` tests a Boolean condition.
3. The indented block runs when the condition is true.
4. An **f-string**, `f"..."`, inserts expressions from inside `{}`.

## 2. What happens when Python runs

For a `.py` script, Python generally parses the source, compiles it to bytecode, and executes that bytecode in the Python runtime. You do not normally compile manually.

Run an example from a terminal:

```bash
python examples/course_workspace_planner.py
```

That command starts a process. Normal completion returns `0`; a deliberate data-quality failure can return `1`; an input/configuration failure can return `2`. This is analogous to job status in AutoSys or TWS.

### Syntax means “the shape of valid code”

- Indentation defines blocks; be consistent (four spaces is conventional).
- `#` begins a comment. Explain intent or a surprising constraint, not obvious syntax.
- Names are case-sensitive: `JobName` and `jobname` are different.
- A valid name starts with a letter or underscore and continues with letters, digits, or underscores.
- A **keyword** such as `if`, `for`, or `class` already has language meaning and cannot be a variable name.
- Use descriptive `snake_case`: `failed_records`, not `x`.

Common error:

```python
if failed:
print("failed")
```

Python raises an `IndentationError` because it cannot identify the block owned by `if`.

## 3. Variables are labels on objects

A variable does not permanently “contain” a fixed type. It refers to an object. Reassignment changes what the label refers to:

```python
status = "PENDING"
status = "SUCCESS"
```

After the second line, `status` refers to `"SUCCESS"`. This is unlike a strongly typed relational column in which the column's declared type remains fixed.

### Type conversion

`input()` returns text, even when a user types digits.

```python
raw_count = input("Rows? ")
row_count = int(raw_count)
```

If the sample input is `27`, the output of `print(row_count + 1)` is `28`. If it is `twenty`, `int()` raises `ValueError`. Validate at a boundary:

```python
try:
    row_count = int(raw_count)
except ValueError:
    print("Rows must be a whole number")
```

Do not force every object to be a string simply to avoid type errors; preserve numeric, date, and Boolean meaning.

## 4. Built-in values as a practical toolkit

| Type | Meaning | ETL/data analogy | Example |
| --- | --- | --- | --- |
| `int` | Whole number | count, ID (sometimes) | `42` |
| `float` | Decimal approximation | measure or ratio | `98.6` |
| `complex` | Real + imaginary part | specialized numeric work | `2 + 3j` |
| `bool` | `True` or `False` | flag / condition | `True` |
| `str` | Immutable text | `VARCHAR`-like value | `"PPE-01"` |
| `tuple` | Fixed ordered values | fixed schema/record | `("INC-1", 2)` |
| `list` | Mutable ordered values | ordered staging list | `[1, 2, 3]` |
| `dict` | Key-to-value mapping | lookup table / JSON object | `{"status": "OK"}` |
| `set` | Unique unordered values | set of keys | `{"A", "B"}` |

### Numeric values

`/` produces a float division result; `//` performs floor division; `%` gives the remainder.

```python
print(7 / 2)   # 3.5
print(7 // 2)  # 3
print(7 % 2)   # 1
```

Be cautious with binary floating-point values:

```python
print(0.1 + 0.2)  # 0.30000000000000004
```

For money, use the `decimal` module when exact decimal arithmetic is required; do not round early at each pipeline step.

### Strings

Strings support slicing and methods but cannot be changed in place.

```python
job = "  nightly load  "
clean = job.strip().upper()
print(clean)       # NIGHTLY LOAD
print(clean[:7])   # NIGHTLY
```

**Important terminology:** the method returns a new value. “`strip()` cleaned the string” is shorthand; technically `job` remains unchanged.

Use `str.splitlines()` for log text, `str.partition()` for a first separator, and `f"{value:.2f}"` for display formatting.

### Tuples and lists

A tuple is useful for a record whose shape should not change:

```python
location = ("eu", "primary")
```

A list is useful when rows are accumulated:

```python
errors = []
errors.append("missing region")
```

Do not choose a tuple merely because its values will be unique; uniqueness is a set concern, not an immutability concern.

### Dictionaries

A dictionary supports named fields and fast key lookup:

```python
incident = {"id": "INC-4", "severity": "high"}
print(incident["severity"])       # high
print(incident.get("owner"))      # None
```

`incident["owner"]` raises `KeyError` if the key is absent. `get()` is appropriate when absence is an expected condition; a strict required-field read should often use brackets so missing data is visible.

### Sets

Sets model membership and uniqueness:

```python
expected = {"id", "status", "region"}
actual = {"id", "status", "extra"}
print(expected - actual)  # {'region'}
print(actual - expected)  # {'extra'}
```

This resembles a schema comparison. Do not depend on iteration order unless the values are explicitly sorted.

## 5. Mutability, aliases, and copies

**Mutable** means the object can be changed. Two names can refer to the same list:

```python
source = ["A", "B"]
alias = source
alias.append("C")
print(source)  # ['A', 'B', 'C']
```

This surprises ETL learners who expect assignment to create a second dataset. It creates a second label, not a second list. Use `source.copy()` for an independent shallow list copy. For nested mutable values, consider `copy.deepcopy()`.

Strings, tuples, numbers, and `frozenset` are immutable. Safe-to-share immutable records can reduce accidental modification.

## 6. Operators and precedence

Python evaluates arithmetic before comparisons, and parentheses make intent explicit.

```python
result = 3 + 2 * 5
print(result)  # 13
```

The comparison `1 < count <= 10` is valid and means `count > 1 and count <= 10`.

### Equality, identity, and membership

- `==` compares values.
- `is` compares whether two labels refer to the exact same object.
- Use `is None` for the common identity check; do not use `is 10`.
- `in` tests membership.

```python
severity = "high"
print(severity == "high")              # True
print(severity in {"high", "critical"}) # True
print(None is None)                    # True
```

### Boolean logic and short-circuiting

`and` and `or` stop once the result is known:

```python
owner = record.get("owner")
valid = owner is not None and owner.strip() != ""
```

If `owner` is `None`, the right side does not run, avoiding an error. The result of `and`/`or` is an operand, although `if` interprets it for truthiness.

Avoid `if value == True`; prefer `if value:`, and use `is False` only where exact identity is important.

## 7. Formatting and auditable output

Use f-strings for readable output:

```python
duration = 8.347
print(f"Elapsed: {duration:.2f}s")
```

Output:

```text
Elapsed: 8.35s
```

In production, machine-readable output should often be JSON/CSV rather than decorative text. Human-friendly logs and machine-readable reports may be separate artifacts.

## 8. Worked folder-planning flow

The generated `course_workspace_planner.py` models a small planning pipeline:

1. Read JSON or use default course specifications.
2. Validate fields into immutable `CourseSpec` records.
3. Build a deterministic folder plan.
4. Print the plan.
5. Materialize folders only when `--apply` is supplied.

Sample input:

```json
[{"slug":"python_genai","lessons":2,"assets":["video","graphics"]}]
```

Without `--apply`, expected `folder_count` is `4` and the filesystem remains unchanged. A dry run resembles the preview step of an Informatica deployment: calculate proposed work before applying it.

Try an invalid lesson count:

```json
[{"slug":"python_genai","lessons":true}]
```

Python deliberately rejects `True` as an integer in this validation. Otherwise `bool`, a subclass of `int`, could accidentally pass a numeric range check.

## 9. Dataclasses, introduced gently

The planner uses:

```python
@dataclass(frozen=True)
class CourseSpec:
    slug: str
    lessons: int
    assets: tuple[str, ...]
```

Building blocks:

1. A **class** defines a new kind of record.
2. `@dataclass` asks Python to generate common initialization/equality behavior.
3. `frozen=True` prevents simple field reassignment, making the record safer to share.
4. The annotation `tuple[str, ...]` describes “a tuple of strings.”

You do not need dataclasses to use Python, but they remove repetitive constructor code when a workflow needs validated records.

## 10. Debugging checklist

1. **Reproduce:** record the exact command and input.
2. **Read the last relevant line:** the traceback's final exception describes the immediate failure.
3. **Locate the boundary:** shell argument, JSON parse, type conversion, path, or external service?
4. **Inspect types:** temporarily use `print(type(value), repr(value))`.
5. **Check assumptions:** `input()` text, zero-based indexes, exclusive stops, `None`, aliases, and Boolean truthiness.
6. **Reduce the input:** create the smallest case that still fails.
7. **Fix one thing and rerun:** do not change syntax and logic simultaneously.
8. **Check the success and failure paths:** wrong input should fail clearly, not silently succeed.

## 11. Common mistakes

- Treating a Boolean as an intended integer.
- Using a list when a record's order/immutability should be fixed.
- Expecting a method such as `.sort()` or `.strip()` to mutate and return the same useful value.
- Comparing with `is`.
- Forgetting that dictionary/set display order is not a business contract.
- Chasing a later traceback line without looking for the first invalid value.
- Printing secrets while debugging.
- Naming a variable too generically (`data`, `temp`, `x`) to explain its purpose.

## 12. Practice: learn by prediction

### Core

1. Predict and explain `3 + 2 * 5`, `7 // 2`, and `7 % 2`.
2. Build a dictionary for one scheduled job with name, owner, enabled, and dependencies; add two dependencies.
3. Convert a comma-separated string into a sorted list of unique uppercase codes.
4. Write a validation for a row count that rejects `True`, negatives, and decimals.
5. Show how copying a list differs from aliasing it.

### Applied

1. Extend the planner with `duration_minutes`; compute total estimated minutes.
2. Reject whitespace around a slug instead of silently stripping it, and explain why the contract differs.
3. Add a `--format` option, preserving the default JSON behavior.
4. Run valid, malformed, duplicate, and oversized specifications.
5. Create a small input/output table in your notes before running each test.

### Reflection

- Which Python collection corresponds best to a SQL row, a result set, and a lookup table?
- Which analogies are useful but imperfect?
- What state is immutable in the planner, and why is that helpful?

## 13. LMS demonstration walkthrough

**Exact resources:** [demonstration 8609](https://lms.snvaveranda.com/mod/resource/view.php?id=8609) and [companion scripts 15704](https://lms.snvaveranda.com/mod/resource/view.php?id=15704).

### Actual scenario and data

The notebook demonstration is specifically about number kinds and arithmetic/comparison work. The companion scripts broaden the lesson: repeated review text is normalized and classified, model metadata demonstrates built-in types, token counts and unit prices demonstrate arithmetic, and a terminal mini assistant uses a name plus an experience sentence. These are independent small scenarios, not one dataset.

A safe synthetic replacement is:

```text
reviews = ["smooth service", "broken item"]
token_counts = {"input": 1200, "output": 300}
prices_per_million = {"input": 2.0, "output": 8.0}
```

The schema is a list of strings for reviews and a mapping of named numeric values for the model/cost calculation. No downloaded data is necessary.

### Step-by-step beginner workflow

1. Start with `reviews = []` and add one short positive and one short negative string of your own.
2. Predict the lower-case form, then use `in` to locate one indicator word.
3. Create scalar values for integer token count, decimal price, trained flag, and optional URL.
4. Print each value, `type(value)`, and its intended meaning.
5. On paper, apply parentheses to the token-cost formula: convert tokens to millions, multiply by unit price, then add input/output cost.
6. Test `+`, `-`, `*`, `/`, `//`, `%`, comparison, logical, identity, and membership operators one family at a time.
7. Run the mini-assistant flow using synthetic input; do not include personal information.
8. Compare predicted and actual output, and explain which operation produced each changed value.

### Connection to the current examples

`demo-data_types.py` and `demo-operators.py` are original, local counterparts to these demonstrations. `mini_ai_assistant.py` follows the review-input idea. The JSON-driven `course_workspace_planner.py` is an **original extension beyond the LMS demonstration**: it adds schema validation, dataclass records, stable planning, dry runs, and an exit-code contract. None of these files is a copy of the LMS notebook or solution scripts.

### Deliberate practice

Before each run, create an input/expected-output table. Replace an integer with `True`, a negative count, and a decimal; predict whether validation should accept it. Add neutral review text and define an explicit “unknown” branch instead of allowing it to fall into another label. Finally, explain the cost formula without running Python: total cost is unit-conversion followed by multiplication and addition, not token multiplication before unit conversion.
