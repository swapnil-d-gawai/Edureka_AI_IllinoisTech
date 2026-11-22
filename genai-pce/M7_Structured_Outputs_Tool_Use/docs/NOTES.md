# Module 7 Notes: Structured Outputs, Function Calling, and Tool Use

## 1. From language to data

LLMs naturally produce text. Automation usually needs data: fixed field names, types,
ranges, enums, and nested structures. A structured-output contract is like an agreed
interface between Unix job, scheduler, API, or data stage. Both ends must know what is
valid and what a terminal failure means.

Important distinctions:

- **JSON mode:** asks for syntactically valid JSON; it does not define business meaning.
- **Schema validation:** checks fields, types, ranges, enums, and nesting.
- **Structured/constrained decoding:** lets the provider/runtime restrict generated syntax
  or shape; application policy validation is still needed.
- **Semantic/business validation:** verifies identifiers, values, evidence, permissions,
  and consequences.

## 2. A narrow schema

Example incident plan:

```json
{
  "incident_id": "INC-7",
  "severity": "high",
  "summary": "Checkout latency is above the agreed threshold.",
  "needs_human_review": true,
  "tool_request": {
    "tool": "get_metrics",
    "arguments": {"service": "checkout", "minutes": 15}
  }
}
```

Contract rules:

```text
exact five top-level fields
severity in low|medium|high|critical
incident_id and summary are bounded non-empty strings
needs_human_review is a real Boolean
tool request is itself an exact nested object
```

Python's `dict` is dynamic and must be inspected. `structured_router.py` demonstrates
standard-library validators. Dataclasses represent validated domain objects after that
inspection.

## 3. Parse, validate, authorize, execute

Never collapse these stages:

```text
raw model text
   -> parse JSON
   -> exact schema/type validation
   -> domain/evidence policy validation
   -> map tool proposal to allowlist
   -> authorize caller and scope
   -> execute bounded operation
   -> validate/sanitize tool result
   -> feed result to a later model step if needed
```

Model output is untrusted, like a file received from an external source. A parser does
not prove the service name exists, and a string that looks like an order ID does not
prove the user may view that order.

## 4. Validation errors and retry policy

Classify:

1. **syntax:** invalid JSON, wrong quotes, trailing comma;
2. **shape:** missing, extra, or nested field;
3. **type:** `"15"` instead of integer `15`, `"true"` instead of Boolean;
4. **enum/range:** severity unknown or duration outside 1–60;
5. **semantic:** valid service field but nonexistent/unauthorized service;
6. **policy:** output proposes a forbidden or consequential tool.

Only a bounded schema correction is retryable. In Module 7's mock, a first incomplete
response receives validation feedback and the second attempt returns the full shape.
Repeated retries should not be used to guess consequential values; collect evidence or
escalate. The request attempt budget is part of the control contract.

## 5. Tool calling: proposal, not execution

A tool/function call from a model is a proposal:

```text
tool = get_metrics
arguments = service=checkout, minutes=15
```

The application:

- resolves the tool from its own registry;
- rejects unknown names (`run_shell`, SQL strings, arbitrary URLs);
- validates exact argument keys and values;
- checks caller authorization;
- applies rate, timeout, and side-effect policy;
- invokes a pre-existing function rather than dynamic code;
- records audit/correlation information.

The `TOOLS` dictionary in `structured_router.py` is a tiny allowlist. Adding a function
requires code review and a narrow schema, not a prompt update.

## 6. Read tools versus write tools

| Read-only | State-changing |
| --- | --- |
| Still enforce tenant, scope, freshness, rate limits, and injection-safe output | Everything for reads, plus idempotency, confirmation, approval, rollback/compensation, and audit |
| Can expose sensitive data if broadly scoped | Can create direct financial, operational, or privacy impact |
| Usually lower consequence but not “safe by default” | Should not execute from fluent text alone |

For a refund, the model might prepare a proposal. A policy service and authorized
employee approve it; a deterministic refund service receives an idempotent action.

## 7. Tool-loop walkthrough

```text
1. model proposes get_metrics(service, minutes)
2. validator confirms allowed fields/types/range
3. dispatcher authorizes and calls get_metrics
4. result is treated as untrusted evidence
5. result is bounded/redacted and added to context
6. model produces a final answer/proposal
7. final output is validated again
```

Tool output can itself contain injection such as “ignore previous instructions.” It is
data, not a new system prompt. Do not reflect secrets from a tool into the next model
call unless the task requires it.

## 8. Cost and latency

Structured generation may add decoding constraints and a small latency cost. Tool loops
add external wait, more model calls, tokenized results, and failure states. Restrict:

```text
maximum tool rounds
maximum tools per round
argument/result length
end-to-end time
retry attempts
result token budget
```

Narrow schemas generally improve routing and reduce invalid actions. They increase
development effort and can create new refusal/escalation cases; include those in the
metric.

## 9. Worked realistic case

Input asks for an incident plan. Attempt 1:

```json
{"incident_id":"INC-7","severity":"high"}
```

Missing fields and wrong shape are detected. Attempt 2 receives the feedback and returns
the complete schema. The plan is converted into `IncidentPlan`, and `dispatch` permits
only `get_metrics`. The demo then asks for `run_shell`; the unknown tool is blocked with
`PermissionError`. This is the desired distinction between model generation and
application authority.

## 10. Failure analysis

| Symptom | Diagnose |
| --- | --- |
| JSON decode error | Raw response, stop/truncation, syntax, output cap |
| Valid JSON, invalid contract | Exact fields/types, schema version mismatch |
| Schema valid, business value invalid | Identifier/evidence/domain policy checks |
| Unknown tool | Tool-name allowlist/routing or prompt confusion |
| Valid tool invoked twice | Missing idempotency/request state |
| Correct read action rejected | Authorization, tenant scope, rate/timeout |
| Tool result changes instructions | Treat returned content as untrusted and delimited |

## 11. Debugging checklist

1. Store the raw response securely enough to debug, redacting sensitive values.
2. Separate parse, schema, policy, authorization, and execution logs.
3. Test exact missing/extra fields and Python Boolean-versus-integer edge cases.
4. Verify tool registry membership without dynamic command construction.
5. Confirm argument limits and caller/tenant authorization.
6. Replay with a fake tool to test idempotency.
7. Inject hostile tool output and ensure it remains data.
8. Confirm terminal fallback is visible and not reported as success.

## 12. Common misconceptions

- **“Valid JSON means correct.”** It may have invented IDs or wrong business meaning.
- **“The model executes a function call.”** The provider proposes; application code executes.
- **“Broad tool descriptions give flexibility.”** They enlarge incorrect and dangerous action space.
- **“A retry repair is harmless.”** It consumes cost and cannot create missing evidence.
- **“Read-only means public.”** Reads can leak confidential data and must be authorized.
- **“Schema validation handles injection.”** It limits shape; data still needs trust-boundary controls.

## 13. Graded exercises

1. **Schema (15):** Define exact types, ranges, enums, required fields, and unknown-field
   behavior for an order-status plan.
2. **Validation (20):** Create tests for malformed, missing, extra, mistyped, boolean-as-int,
   out-of-range, and policy-invalid values.
3. **Routing (20):** Add a read-only fake tool to a local copy and prove unknown tools and
   dynamic commands remain blocked.
4. **Lab (20):** Run `structured_router.py`; trace both model attempts and the unsafe
   `run_shell` rejection.
5. **Production design (25):** Specify retries, timeouts, idempotency, authorization,
   audit, human approval, and compensation for one state-changing tool.
