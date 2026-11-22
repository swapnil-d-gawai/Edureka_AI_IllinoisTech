# Concurrent vendor monitor

This standard-library-only exercise models an AI-operations dependency monitor. It uses an abstract client, dataclass mock, custom exception, preserving async decorator, bounded concurrency, structured logging, injected failures, and a sequential benchmark.

```bash
python async_vendor_monitor.py
python async_vendor_monitor.py --vendors identity search email --concurrency 2 --verbose
```

No network or external service is used. The mock intentionally fails `payments-gateway`; the report still contains every requested vendor and records the error. `speedup` should exceed 1 for the default independent delays, though timing is machine-dependent.

Challenges: add per-vendor timeouts, exponential retries with jitter, an unstructured log redaction rule, and tests proving the concurrency semaphore never exceeds its limit.

## LMS bridge

LMS resource 8613 moves from classes/inheritance and exception scope to regular expressions and concurrent Groq calls. Run the vendor monitor first with synthetic offline delays, then use the notes to map its `gather`, failure isolation, and timing observations to the LMS Groq exercise. This monitor is an original extension and deliberately does not use a course API key or provider implementation.
