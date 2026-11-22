# Module 3 Notes: Working with LLMs

## 1. A model call is an operational boundary

An application normally calls a hosted API or a locally served model through a client.
Keep provider-specific SDK details in one gateway; business logic should speak in your
own request/response types. This resembles using a standard Informatica connector instead
of embedding vendor SQL and credentials in every mapping.

```text
business workflow
   -> internal gateway request
      -> authentication -> timeout/rate-limit/retry -> provider
      <- text/tool request + usage + stop reason
   <- validate -> business result
```

A `Provider` interface (like the `Protocol` in `llm_gateway.py`) describes what the
workflow needs. A real SDK adapter can replace the offline mock later without changing
the policy logic.

## 2. Request anatomy and roles

A typical chat request contains:

- **system/developer instructions:** trusted task policy and output constraints;
- **user input:** the actual request, untrusted for instruction authority;
- **tool definitions/results:** separate structured capabilities and observations;
- **retrieved context:** quoted source evidence, not new authority;
- **generation settings:** runtime limits and decoding controls;
- **request identity:** correlation, tenant, and idempotency metadata.

Messages are not a security database. If permissions depend on a role string in a
prompt, an attacker can attempt to imitate it. Enforce authorization in code.

## 3. Temperature, top-p, and top-k

| Control | Effect | Safe starting point |
| --- | --- | --- |
| Temperature | Reshapes the next-token distribution; low values favor leading candidates, high values spread probability | Low (`0`–`0.3`) for extraction/classification; task-specific for drafting |
| Top-p (nucleus) | Considers the smallest set of tokens whose cumulative probability reaches `p` | Often `0.9`–`1.0`; avoid stacking changes without testing |
| Top-k | Considers only `k` highest-scoring tokens | Provider/task dependent |
| Max output tokens | Hard upper bound on generated tokens | Large enough for contract, small enough for budget |
| Stop sequence | Ends at configured delimiter | Useful for a structured legacy protocol; validate final output |
| Seed | Requests repeatability where supported | Use in repeatable tests, not as a guarantee across providers |

Imagine candidate tokens with scores:

```text
"approved" 0.55, "review" 0.25, "declined" 0.12, other 0.08
```

Sampling with temperature may still choose “declined”; it cannot verify that policy
permits it. These controls tune **variation**, not truth, authorization, or format.

Provider APIs differ. If a model rejects combined temperature/top-p settings or has
different ranges, the gateway translates your validated internal contract.

## 4. Decoding strategies

- **Greedy:** choose the highest-probability next token. Fast and stable, but one local
  choice can make a later global sequence worse.
- **Beam search:** retain several partial sequences. More compute and memory can improve
  constrained tasks; it does not establish truth.
- **Sampling:** choose from a distribution. Useful for brainstorming and multiple
  hypotheses; problematic for regression tests.
- **Constrained decoding:** restrict output grammar or schema. Strong for format, but
  schema-valid content can still be factually or policy-invalid.

For extraction, prefer a strict schema plus deterministic/low-sampling behavior. For
ideation, diversity may be a requirement. Write both criteria into the benchmark.

## 5. Tokens, max output, and a cost walkthrough

The context budget includes every input plus output. A simple approximation in the
offline example is four characters per token; this is only an educational estimate.
Actual values come from the provider/model tokenizer and usage response.

Example:

```text
input:  8,000 tokens at versioned rate I
output:   300 tokens at versioned rate O
request estimate = 8,000*I + 300*O
daily  = request estimate * successful calls (include retries separately)
```

`llm_gateway.py` uses illustrative rates and deliberately prints usage. Production
pricing is configuration with an effective date. Re-price model changes and retries;
output tokens may cost more than input tokens.

## 6. Timeouts, retries, and control flow

Treat errors as distinct TWS/AutoSys completion states:

| Error | Retry? | Action |
| --- | --- | --- |
| HTTP 429/rate limit | Usually | Bounded exponential backoff with jitter; respect retry-after |
| Timeout/network reset | Sometimes | Retry only if duplicate downstream effects are impossible |
| 401/403/auth | No | Alert configuration owner |
| Invalid request/schema | No | Fix caller or output contract |
| Content/policy refusal | No blind retry | Apply safe fallback or alternate approved workflow |
| Malformed model content | Limited | Schema repair/one feedback retry, then escalate |
| Safety/policy validation failure | No | Block, record, human review |

Example retry trace:

```text
attempt 1 -> 429 -> wait 10 ms
attempt 2 -> 429 -> wait 20 ms
attempt 3 -> valid completion -> validate -> return
```

A timeout must cover the full provider call and the application deadline. Retrying a
request that already caused a write could create duplicates. Put idempotency keys on
state-changing operations, but keep generation retries separate from tools that have
side effects.

## 7. Hosted API versus local deployment

| Dimension | Hosted | Local/open-weight |
| --- | --- | --- |
| Startup | Fast; no training infrastructure | Hardware, runtime, model packaging, patching |
| Data control | Contract and region controls matter | Data can remain inside your environment |
| Scaling | Provider handles capacity within quotas | You own autoscaling, queues, and accelerator utilization |
| Pricing | Metered/contract usage | Hardware and engineering cost; marginal call not “free” |
| Reliability | Provider outages/rate limits | Node, runtime, load, and model failures |
| Versions | Can retire/change independently | You pin and operate exact artifact |

Neither option removes evaluation. Local deployment can still produce unsupported facts.
Hosted operation can still be secure if controls meet requirements.

## 8. Worked gateway flow

**Input**

```text
request_id=req-17
task: concise evidence-based support assessment
observation: delayed shipment; customer requests escalation
settings: temperature=0.2, top_p=0.9, max_tokens=180, timeout=5s
```

`llm_gateway.py` simulates two transient throttles and succeeds on the third call.

**Output**

```text
Incident triage complete: verify policy evidence before taking action.
attempts=3
input/output token estimates and elapsed time included
```

A second provider deliberately returns malformed JSON. Parsing occurs outside the
provider, fails, and terminates through a safe catch. The demo prints an escalation; it
does not silently convert `{... ,}` into business data.

## 9. Reliability, observability, and privacy

Log a request ID, tenant, model/version, prompt/config version, retry count, latency,
token usage, stop reason, validation result, and terminal business state. Avoid logging
secrets and raw personal or customer content by default. Hash or redact where needed and
apply retention limits.

Dashboard at three levels:

1. **service:** availability, p95/p99 latency, throttles, timeouts, circuit state;
2. **quality:** validity, task score, abstention, source correctness;
3. **business:** escalation rate, resolved outcome, fairness slices, cost per success.

## 10. Failure analysis

Use the following as a debugging checklist for any failed request:

1. Was the request accepted by the provider?
2. Did it terminate, time out, or get throttled?
3. What was the stop reason and token count?
4. Does the raw output match syntax and schema?
5. Does the validated value match approved evidence and policy?
6. Did retries or fallbacks preserve idempotency?
7. Did logging expose sensitive input?

Do not “fix” every provider failure with an uncapped `while True`. That is the equivalent
of an AutoSys retry loop that can duplicate work and consume the entire budget.

## 11. Common misconceptions

- **“Temperature 0 is deterministic everywhere.”** Provider, backend, and model changes
  can still change results.
- **“One successful call is enough testing.”** Repeat for long, malformed, rate-limited,
  unavailable, and policy-invalid cases.
- **“A context-length model can safely accept that many input tokens.”** Leave room for
  output, tool messages, and application overhead.
- **“Retrying is harmless.”** It multiplies cost and can duplicate side effects.
- **“Local means no operations.”** You own capacity, patching, and hardware failure.
- **“The SDK is the architecture.”** Put business contracts behind a narrow interface.

## 12. Graded exercises

1. **Parameters (15):** Describe what temperature, top-p, max tokens, and stop do; label
   which affect choice diversity, cost, and termination.
2. **Cost (15):** Build an input/output/retry cost table for 10,000 requests. State which
   provider price fields need versioning.
3. **Reliability (25):** Classify ten sample failures as retry, fix, escalate, or block.
4. **Lab (20):** Run `llm_gateway.py`; explain the third-attempt success and malformed
   output path from entry to terminal state.
5. **Architecture (25):** Design a gateway interface and telemetry record for one hosted
   and one local provider without putting credentials in code.

## 13. LMS demonstration walkthrough

Open `https://lms.snvaveranda.com/mod/resource/view.php?id=8631`. The actual
developer-lab scenarios cover three distinct interfaces:

- Configure Gemini, discover supported models/limits, send explanation, code,
  translation, and general prompts, inspect response candidates, finish
  reason, and safety metadata, and run multi-turn chat.
- Compare creative-generation controls—temperature, top-p, top-k, maximum
  output tokens, and stop sequences—while holding model/prompt constant.
- Estimate prompt tokens, compare verbose/concise requests, trim context, and
  contrast individual and batched requests.

The input schema is a prompt plus model identifier and generation settings;
chat adds ordered turns. Expected outputs are text, status/finish information,
length or estimated token measurements, and explicit errors for missing
credentials, invalid/empty input, rate limits, or limits. The generated prose
will vary, so tests should check constraints and evidence rather than exact
wording.

A beginner workflow maps the call to a controlled external lookup:

1. Load the credential from the process environment and fail closed if absent.
2. Discover the model and read its input/output limits like a source-system
   contract.
3. Start with one short generation and log request ID, latency, and usage but
   not the key or sensitive prompt.
4. Add bounded backoff for retryable failures and immediate escalation for
   malformed or policy-blocked results.
5. Change one parameter at a time and compare prompt/output totals, not only
   subjective style.

The default is `examples/llm_gateway.py`: its `MockProvider`, deterministic
throttle, and malformed structured response reproduce operational paths
offline. This is the current original example and is the abstraction the LMS
Gemini adapter would fit behind; it does not pretend that a mock measures real
provider safety or tokenization.

For deliberate practice, define a release test for 50-token and 150-token
limits, predict the effect of low versus high top-p, and record retry count,
finish reason, latency, estimated cost, and validation result. Provider
execution is optional; a learner can complete the entire reasoning and mock
workflow offline.
