# Module 3 Notes: Advanced Python Concepts

This module follows the LMS coverage of decorators, classes and objects, inheritance, polymorphism, exceptions/logging, modules and packages, JSON/CSV, and `asyncio`. “Advanced” mainly means combining previously learned building blocks while making failure behavior explicit.

## 1. Objects: state plus behavior

A **class** describes a type; an **instance/object** is one concrete value of that type.

```python
class Job:
    def __init__(self, name):
        self.name = name

    def display_name(self):
        return self.name.upper()

job = Job("load_customers")
print(job.display_name())  # LOAD_CUSTOMERS
```

- `__init__` initializes a new object.
- `self` refers to the particular instance.
- `display_name` is a method (a function attached to the class).

This resembles a record plus related operations. Keep each class focused; a class named `System` that validates, transforms, calls APIs, and writes files is difficult to test.

## 2. Dataclasses without the mystery

A dataclass generates repetitive code:

```python
@dataclass(frozen=True)
class ClientConfig:
    seed: int = 17
```

Building blocks:

1. `@` applies a **decorator**.
2. `@dataclass` inspects annotated fields and generates methods such as `__init__`.
3. `frozen=True` prevents normal field reassignment.

It does not validate values automatically and is not database persistence.

## 3. Decorators: a function receiving a function

```python
def trace(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        print(f"starting {function.__name__}")
        return function(*args, **kwargs)
    return wrapper

@trace
def transform():
    return "done"
```

`transform()` is now equivalent to calling the wrapper returned by `trace`. `*args` and `**kwargs` let the wrapper accept the original function's positional and named arguments. `functools.wraps` copies metadata such as the function name and docstring.

Correct decorator contracts:

- preserve arguments,
- await an async target when wrapping one,
- return the target result,
- preserve exceptions unless policy says otherwise,
- avoid hidden retries with side effects.

Common use cases are timing, logging, authorization, validation, caching, and bounded retries. These are **cross-cutting concerns**, analogous to a scheduler wrapper around a business executable.

## 4. Inheritance, composition, and polymorphism

**Inheritance** models “is a”: `DatabaseVendor` may be a kind of `VendorClient`. It should hold a genuine subtype relationship.

**Composition** models “has a”: a monitor has a retry policy and client. Prefer composition when responsibilities can vary independently.

**Polymorphism** lets callers use a stable operation while implementations differ:

```python
result = await client.check("identity")
```

`client` might be a mock, HTTP client, or production provider; the caller only needs the `check` contract.

Abstract base classes (`ABC`, `@abstractmethod`) make a required method explicit. A duck-typed protocol can be even more flexible, but either approach should define inputs, outputs, and failure behavior.

## 5. Exception handling as workflow routing

An exception is not merely a log message. It transfers control to the nearest handler.

```python
try:
    value = parse_record(raw)
except json.JSONDecodeError as exc:
    quarantine(raw, str(exc))
```

Catch the narrow exception you can meaningfully handle. Catching `Exception` and returning success hides defects, similar to marking a failed ETL mapping as successful.

### Custom domain exceptions

```python
class VendorError(RuntimeError):
    """A vendor could not provide a usable result."""
```

Create a custom exception when callers need a stable domain concept. Keep the low-level cause:

```python
try:
    call_vendor()
except TimeoutError as exc:
    raise VendorError("vendor timed out") from exc
```

`raise ... from ...` preserves the causal traceback.

### `finally` and context managers

`finally` runs during normal exit and most exceptional exits:

```python
handle = acquire()
try:
    use(handle)
finally:
    release(handle)
```

Prefer `with` when a type implements a context manager. It encodes this cleanup pattern and reduces forgotten release paths.

## 6. Logging for operations

Logging should answer: which operation, identifier, outcome, elapsed time, and actionable reason?

```python
LOGGER.warning("vendor check failed vendor=%s", vendor)
```

Benefits:

- timestamps and levels can be configured centrally,
- records can go to stdout, files, or log collectors,
- lazy `%s` formatting avoids building a message when the level is disabled.

Use `DEBUG` for detailed diagnostics, `INFO` for lifecycle outcomes, `WARNING` for degraded but handled work, and `ERROR`/`EXCEPTION` for failures. Never log credentials, secret prompts, or full personal payloads.

Printing is suitable for a learner's final command output, but structured logging is generally better for running services.

## 7. Modules, packages, and dependencies

A **module** is usually a `.py` file. A **package** organizes modules, traditionally with `__init__.py`.

```python
from pathlib import Path
```

Avoid wildcard imports because they obscure names and coupling. Use relative imports within a package only when the package layout is clear; direct script execution and package execution resolve imports differently.

Dependencies should be declared in a project manifest such as `requirements.txt` or `pyproject.toml`. Pin or constrain versions when reproducibility matters. An isolated virtual environment prevents one course/app from changing another app's library versions—similar to separating Informatica runtime environments.

## 8. JSON versus CSV

JSON preserves nested objects, arrays, numbers, Booleans, and text:

```python
record = json.loads('{"id":"INC-1","labels":["data"]}')
```

CSV is a rectangular table:

```text
id,kind
INC-1,data
```

Use `csv.DictReader` for CSV with quoting/newlines and `newline=""`; do not split on commas because valid CSV fields may contain commas and escaped quotes.

After parsing, values still need validation. JSON numbers are not necessarily the intended integer range; CSV values begin as strings.

## 9. Async: overlapping waits

`async def` creates a coroutine function. Calling it returns a coroutine; `await` actually drives it.

```python
async def fetch():
    await asyncio.sleep(1)
    return "ready"
```

`await` yields control while work is waiting, allowing other I/O tasks to run. This is useful for many independent API/database waits. It does not parallelize CPU-heavy Python calculations.

A scheduler analogy: concurrency resembles multiple jobs that can run while waiting on remote dependencies. The number of slots and the critical path still matter.

### Sequential versus concurrent

```python
sequential = [await fetch(vendor) for vendor in vendors]
concurrent = await asyncio.gather(*(fetch(vendor) for vendor in vendors))
```

Input: three independent one-second waits.

Expected shape: sequential is about three seconds; concurrent is about one second. Both return three results.

Real speedups are machine/network dependent. `gather()` with `return_exceptions=True` can collect failures, or each task can translate an expected exception into a result as `safe_check()` does.

### Bound concurrency

Unbounded concurrency can overload providers. A semaphore is a small permission pool:

```python
async with semaphore:
    result = await call_vendor()
```

The vendor monitor sets a limit, validates it, and uses `Semaphore`. This resembles configured AutoSys concurrent-job slots.

### Idempotency and retries

**Idempotent** means repeating an operation has the intended same effect. Retrying a read is usually safer than retrying “charge payment.” Any retry policy needs bounded attempts, delay, exception selection, and side-effect awareness.

## 10. Generic type and decorator syntax in the example

`ParamSpec`, `TypeVar`, `Callable`, and `Awaitable` describe the async decorator's shape for static analysis. They do not change runtime speed or values.

Conceptually:

- `P` represents the wrapped function's parameter list.
- `R` represents its awaited result.
- `Callable[P, Awaitable[R]]` means a callable that takes `P` and returns an awaitable result `R`.

If this syntax obscures the lesson, first understand a simple decorator, then add the annotations.

## 11. Vendor-monitor walkthrough

`async_vendor_monitor.py` proceeds through these stages:

1. Validate vendor names and concurrency limit.
2. Construct a deterministic mock client.
3. Run all vendor checks sequentially.
4. Run the same checks concurrently.
5. Convert an expected `VendorError` into a failed result for that vendor.
6. Keep logging and timing outside the report contract.
7. Measure and report speedup plus result parity.

`payments-gateway` intentionally fails. Sample conceptual summary:

```json
{
  "healthy_count": 4,
  "result_parity": true
}
```

One random-health result may vary only if parameters or implementation change; seeded behavior here is deterministic for a vendor name.

## 12. Debugging async code

1. Check for a runtime warning such as “coroutine was never awaited”; add the intended `await`.
2. Ensure `asyncio.run()` is called at the top-level synchronous boundary, not inside an already running event loop.
3. Never block the loop with `time.sleep()`; use `asyncio.sleep()` for demonstration and non-blocking clients for real I/O.
4. Add timeouts to external waits.
5. Verify semaphore limits and avoid holding one during unrelated CPU work.
6. Log task/vendor identifiers.
7. Keep failures visible in structured results.
8. Measure elapsed time repeatedly; one run is not a benchmark.

## 13. Common mistakes

- Writing a decorator that loses the original return value.
- Forgetting to `await` an async function.
- Treating concurrency as free.
- Retrying a non-idempotent write.
- Catching and ignoring all exceptions.
- Logging secrets.
- Deep multiple-inheritance trees.
- Mixing sync blocking I/O into an async route.
- Benchmarking a single tiny run.

## 14. Practice

1. Wrap a normal function with a timing decorator and use `wraps`.
2. Wrap an async function; verify the wrapper awaits and returns the result.
3. Add a per-vendor timeout with a deterministic failure.
4. Compare `gather()` with sequential execution for three simulated delays.
5. Design a protocol for `check`; list exact success and failure fields.
6. Write JSONL with one valid and one invalid row, then CSV with quoted commas.
7. Add a retry only to the read-like vendor health check and justify its limit.
8. Test that the semaphore never permits more than its configured number of active calls.

## 15. LMS demonstration walkthrough

**Exact resource:** [demonstration 8613](https://lms.snvaveranda.com/mod/resource/view.php?id=8613).

### Actual scenario and data

The demonstration collection covers object/class identity and scope; single/multiple inheritance and method resolution; a banking-style customer/privileged-customer amount calculation; standard modules/imports and path/system functions; exceptions, `finally`, propagation, and custom exceptions; regular-expression search/matching/replacement; and a final Groq `asyncio` timing exercise over multiple independent prompts.

Use synthetic records rather than the archive's examples:

```text
Customer(id="C-2", name="Sample User", kind="standard", principal=1000)
prompts = ["summarize item A", "classify item B", "extract terms from item C"]
```

The input contract should separate business fields from provider configuration. A real Groq run additionally needs a locally configured key; it is not data for the repository.

### Step-by-step beginner workflow

1. Define one class with immutable-looking input fields and one behavior.
2. Instantiate twice; inspect instance and class values separately to understand scope.
3. Add one child class and draw “parent → child”; only then try multiple inheritance and inspect method resolution.
4. Calculate regular and privileged outputs from your own principal/rate before coding the branch.
5. Place a division-conversion failure inside `try`; catch the narrow expected exception and ensure cleanup runs in `finally`.
6. Apply a simple regex to one invented identifier; test matching, non-matching, and replacement separately.
7. Model three provider calls with local `asyncio.sleep` delays. Run sequentially, then concurrently with `gather`.
8. Record status for every coroutine, add one deliberate failure, and confirm other results remain visible.
9. Only after the offline flow is correct, replace the local delay with a provider adapter that reads its key from the environment and has a timeout.

### Connection to the current examples

`demo-class.py`, `inheritence_demo.py`, and `ExcepHandling_Logging_demo.py` support the classroom concepts. `async_vendor_monitor.py` is an **offline original extension beyond the LMS Groq demo**: it adds a replaceable client interface, custom domain exception, bounded semaphore, structured result, and sequential/concurrent parity check. It therefore teaches concurrency without requiring or emulating copied LMS provider code.

### Deliberate practice

Predict the output of a customer amount calculation before running. Force one non-numeric value, one missing mapping key, one regex mismatch, and one async failure. Require the caller to see the failure reason rather than an empty result. Change the three delays and state which workflow has the larger expected wall-clock time and why. Timing measurements are evidence from one run, not a universal performance promise.
