# Module 3 exercise: provider-agnostic LLM gateway

`llm_gateway.py` simulates an industrial LLM client with validated generation settings, an interchangeable provider protocol, token/cost estimates, timeouts, and retry handling. It deterministically simulates transient throttling and a malformed structured result.

## Run

```bash
cd genai-pce/M3_Working_with_LLMs/examples
python llm_gateway.py
```

Default execution is offline and uses `MockProvider`; no credentials or network access are needed. It prints successful retry behavior and a validation failure that escalates instead of silently accepting malformed output.

## Extensions

- Add an optional SDK adapter that reads configuration from environment variables.
- Track p50/p95 latency and token usage in a JSON metrics file.
- Implement per-provider retries, circuit breaking, and idempotency keys.
- Add a schema field to the request and validate JSON responses after provider calls.
