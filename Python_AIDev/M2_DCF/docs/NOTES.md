# Module 2 Notes: Data Structures, Control Flow, and File Operations

These notes follow the LMS deck map for loops, loop control, `match`, user input, files, sequences, collections, `range`, `bytes`, and `bytearray`. Control flow chooses what happens; data structures determine how work is represented.

## 1. A mental model for batch processing

Think of a Python batch as a small ETL mapping:

1. **Source:** read a file, shell argument, or API response.
2. **Router:** decide which case or rule applies.
3. **Transformation:** validate and normalize.
4. **Reject path:** keep reason and source context.
5. **Sink:** write a report or enriched record.
6. **Status:** return an exit code to AutoSys/TWS.

The Unix pipeline idea `read -> filter -> write` is useful. Python makes each stage explicit and testable.

## 2. Conditions and blocks

A condition evaluates a value as true-like or false-like:

```python
if rejected:
    print("batch has rejects")
elif loaded == 0:
    print("batch is empty")
else:
    print("batch accepted")
```

`False`, `None`, `0`, `0.0`, and empty collections/strings are false-like; most other values are true-like. Prefer explicit checks for business clarity when a value could legitimately be zero.

## 3. `for`, `while`, and progress

Use `for` for a known iterable:

```python
for row_number, row in enumerate(rows, start=1):
    print(row_number, row)
```

This resembles processing every result row, but the iterable controls where rows come from. `enumerate()` adds a counter without maintaining one manually.

Use `while` when progress depends on a changing condition:

```python
attempt = 1
while attempt <= 3:
    if try_job():
        break
    attempt += 1
```

Always identify what makes a `while` loop terminate. A missing `attempt += 1` can consume CPU indefinitely, unlike a scheduler that may enforce a timeout.

### `break`, `continue`, and `pass`

- `break` exits the nearest loop.
- `continue` skips to the next iteration.
- `pass` does nothing; it is a placeholder, not a skip instruction.

```python
for item in events:
    if not item:
        continue
    if item["kind"] == "shutdown":
        break
    process(item)
```

### `for ... else`

Loop `else` runs if the loop completed without `break`:

```python
for customer in customers:
    if customer["id"] == target_id:
        print(customer)
        break
else:
    print("not found")
```

The mental model is “search exhausted without a match.” It does not mean the loop ran zero times or that an `if` was false.

## 4. Structural pattern matching

`match` selects by a value's shape. A tagged event is a good use:

```python
match event:
    case {"kind": "service", "region": region}:
        queue = ("service", region)
    case {"kind": "security", "indicator_count": count}:
        queue = ("security", count)
    case _:
        raise ValueError("unknown event")
```

Sample input:

```json
{"kind":"service","region":"eu"}
```

Result:

```python
("service", "eu")
```

Use capture names such as `region` deliberately. `_` is the wildcard. A mapping pattern checks the required keys but normally permits extra keys; add explicit policy if unknown keys must be rejected.

Compared with a long `if/isinstance` chain, matching makes the accepted message shapes visible. Compared with a formal data-validation library, it still requires explicit field-value checks.

## 5. Interactive input and safe conversion

`input("Count: ")` always returns `str`.

```python
raw = input("Count: ")
try:
    count = int(raw)
except ValueError:
    print("Count must be an integer")
```

Never use `eval()` to parse user data. For `3`, `eval()` returns a number, but the caller could execute Python expressions. Use `int()`, `float()`, `json.loads()`, or a parser designed for the format.

For automation, command-line arguments or environment variables are usually better than waiting for interactive input.

## 6. File operations

Use a context manager:

```python
with path.open("r", encoding="utf-8") as stream:
    for line in stream:
        print(line.rstrip())
```

The `with` statement closes the file even when processing raises an exception. This is similar to ensuring a Unix file descriptor is released during every job exit path.

### File modes

| Mode | Meaning |
| --- | --- |
| `r` | read existing text |
| `w` | create/truncate; deletes old content |
| `a` | append to existing or new text |
| `x` | create only; fail if present |
| `b` | combine with mode for raw bytes |
| `+` | combine with mode for reading and writing |

Be explicit about encoding: UTF-8 is a portable text default. Newline handling matters for CSV opened through `csv`; use `newline=""` there.

### Paths

`pathlib.Path` joins components without guessing slash direction:

```python
report = Path("reports") / "2026-11-22" / "summary.json"
```

Do not concatenate paths with manual `/`, especially for cross-platform code.

### Atomic-style replacement

The incident example writes an adjacent `.pending` file, then renames it:

```python
temporary.write_text(...)
temporary.replace(output)
```

If serialization succeeds but a later process interruption occurs, the previous final report is less likely to be mistaken for a partial write. Full durability also depends on filesystem semantics.

## 7. Sequences: order with a position

A **sequence** provides ordered members that may be accessed by index. Indexes begin at `0`; negative indexes count from the end.

```python
statuses = ["NEW", "RUNNING", "DONE"]
print(statuses[0])   # NEW
print(statuses[-1])  # DONE
```

### Slicing

The stop index is exclusive:

```python
values = [10, 20, 30, 40]
print(values[1:3])   # [20, 30]
print(values[::2])   # [10, 30]
```

`values[:]` makes a shallow copy. A slice of nested objects copies the outer container, not the nested objects.

### Concatenation and repetition

```python
print([1, 2] + [3])  # [1, 2, 3]
print(["x"] * 3)     # ['x', 'x', 'x']
```

Repetition duplicates references. With nested mutable lists, prefer a comprehension to create independent sublists.

## 8. Choose the collection that matches the rule

| Need | Collection |
| --- | --- |
| preserve row order and mutate | `list` |
| fixed boundary record | `tuple` |
| unique values or membership | `set` / `frozenset` |
| lookup by a named/typed key | `dict` |
| ordered immutable text | `str` |

### Lists

`append` adds one member; `extend` adds members from an iterable.

```python
queues = ["normal"]
queues.extend(["security", "data"])
```

Do not modify a list while iterating it unless the mutation behavior is carefully designed. Build a filtered list or iterate over `list(original)`.

Sorting in place:

```python
queues.sort()
```

returns `None` and changes `queues`. Sorted copy:

```python
ordered = sorted(queues)
```

returns a new list.

### Tuples

Tuples document fixed grouping, such as `(queue, detail)`. They are hashable if every member is hashable, which allows them to be dictionary keys.

### Sets

```python
source_ids = {"A", "B", "A"}
print(source_ids)       # unique values; output order is not contractual
print("A" in source_ids)
```

Operations:

- `a | b`: union
- `a & b`: intersection
- `a - b`: values in `a` only
- `a ^ b`: values in exactly one set

### Dictionaries

Methods commonly used in ETL work:

```python
record.get("owner")                  # None when absent
record.setdefault("attempts", 0)     # insert default only if absent
record.keys()
record.values()
record.items()
record.pop("temporary")             # remove and return
```

A dictionary key must be hashable and unique. JSON-like nested dictionaries are useful but can become difficult to validate without a defined schema.

## 9. `range`, bytes, and byte arrays

`range(start, stop, step)` is lazy: it describes values without allocating a list. Stop is exclusive.

```python
list(range(1, 10, 3))  # [1, 4, 7]
```

`bytes` stores immutable binary values:

```python
payload = b"OK"
```

`bytearray` is mutable and useful for low-level edits. Text decoding is separate:

```python
text = payload.decode("utf-8")
```

Reading a log as binary and decoding later is sometimes needed, but for ordinary UTF-8 text open it as text and pass the encoding explicitly.

## 10. Complete incident-batch example

Input lines:

```text
{"id":"INC-100","kind":"service","severity":"critical","region":"eu"}
{"id":"BAD","kind":"data","severity":"low","rows_affected":-1}
```

Expected conceptual output:

- First row: accepted into `page-on-call`, detail `eu`.
- Second row: rejected with `invalid data incident`.
- Process exit: `1`, because the batch has valid work plus rejects.

Why `1` rather than `2`? The script distinguishes data-quality findings from an unreadable file or unexpected I/O failure.

The duplicate-removal stage intentionally occurs after per-line classification. It preserves the first accepted record by ID and rejects later duplicates, an explicit deduplication policy akin to SQL `ROW_NUMBER()`.

## 11. Debugging checklist

1. Print or log `line_number` and a shortened raw record, not an entire confidential payload.
2. Check actual types before operations: `json.loads()` may yield a list, number, or string, not necessarily a dictionary.
3. For no output, verify the condition and iterable rather than the `print` itself.
4. For off-by-one errors, draw indexes and the exclusive stop.
5. For path errors, check `Path.cwd()`, existence, spelling, and permissions.
6. For a silent file overwrite, confirm `w` versus `a`.
7. For an infinite loop, verify every branch makes progress.
8. Re-run a clean minimal input separately from a malformed case.

## 12. Common mistakes

- Forgetting Python starts indexes at zero.
- Treating `range(5)` as including `5`.
- Using `eval()` on untrusted values.
- Parsing JSON as if it is always an object.
- Opening with `"w"` while intending `"a"`.
- Modifying a collection during iteration.
- Using a list as a dictionary key.
- Ignoring encoding or line endings.
- Assuming set/dictionary order will remain meaningful.

## 13. Practice

1. Write both `for` and `while` versions that count through 10; explain the termination rule.
2. Classify three JSON event kinds with `match`, including a `_` reject case.
3. Given a result list, find missing and unexpected required IDs with set difference.
4. Read a text file safely and report blank lines with line numbers.
5. Extend the incident example for maintenance records and test one unknown shape.
6. Write a separate rejected-only report while retaining stable input order.
7. Test empty file, missing file, one malformed line, duplicate ID, and all-clean input.
8. Explain why a pending-file replacement is helpful but does not replace backup/retention policy.
