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

## LMS bridge and optional provider practice

The LMS resource (`8631`) uses Gemini for model discovery, basic/chat calls,
generation-control experiments, error handling, and token optimization. This
gateway is the offline bridge to that lifecycle. For optional live practice,
implement the existing provider interface in a separate adapter, read the key
from the environment, set a small output cap and timeout, and never enable it
by default. Reuse the mock's validators, retry policy, telemetry, and
malformed-output gate rather than bypassing them.

The data-pipeline/SQL/Informatica/Unix background is a teaching analogy, not a
constraint on API, SDK, chat, generation-parameter, or optimization breadth.
