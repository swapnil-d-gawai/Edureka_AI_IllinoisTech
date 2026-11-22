# Module 4 Notes: Prompt Engineering Essentials

## 1. What a prompt is

A prompt is a versioned runtime specification, not a magic sentence. It converts a
business task into instructions, bounded context, examples, exclusions, and an output
contract. In ETL terms, prompt engineering defines a transformation contract; the example
benchmark proves the contract against representative input.

The most useful prompt specification has:

1. **Goal:** one observable result.
2. **Audience/task context:** what the result is for.
3. **Trusted rules:** allowed labels, facts, and behavior.
4. **Untrusted inputs:** clearly delimited user/document data.
5. **Output contract:** exact shape or allowed values.
6. **Missing-evidence rule:** abstain/escalate rather than invent.
7. **Examples:** only where they resolve meaningful ambiguity.

## 2. Instruction placement and roles

Use system/developer instructions for policy and task constraints. Put customer text,
documents, and history in separately labeled data fields. A tag such as:

```text
<untrusted_customer_text>
Please ignore the prior instructions...
</untrusted_customer_text>
```

does not make the content safe by itself. It makes the boundary visible and helps the
application inspect it. Model role wording (“you are an expert”) can set tone, but it
does not grant database access, knowledge, or authority.

Avoid contradictory instructions. A “be concise” instruction followed by ten paragraphs
of mandatory caveats invites context competition.

## 3. Zero-shot, one-shot, and few-shot

| Pattern | Description | When to use | Cost/risk |
| --- | --- | --- | --- |
| Zero-shot | No demonstrations | Clear, familiar, stable task | Lowest token cost; format may be ambiguous |
| One-shot | One canonical demonstration | Simple tone or mapping convention | One case can become over-influential |
| Few-shot | Several balanced demonstrations | Important edge cases or output variants | More tokens, bias, privacy, possible overfitting |

Choose examples that cover boundaries:

```text
Input: "charged twice"          -> billing
Input: "tracking has not moved" -> delivery
Input: "something is wrong"     -> uncertain
```

The “uncertain” example is important. The model needs a demonstrated safe path when
evidence is insufficient. More examples are not automatically better.

## 4. Prompt template walkthrough

**Template**

```text
Task: classify a support ticket using the policy below.
Allowed labels: billing, delivery, technical, uncertain.
Rules: choose uncertain if evidence is insufficient.
Output: exactly one label; no explanation.
Examples: ...
<untrusted_customer_text>{{ticket}}</untrusted_customer_text>
```

**Input**

```text
The courier lost the parcel
```

**Expected output**

```text
delivery
```

For `I opened the app and it looks unusual`, `uncertain` is safer than guessing
`technical`. A test suite must value correct abstention, not only raw label accuracy.

## 5. Building a prompt specification

Define it before tuning:

```text
name: support-route-v3
input schema: ticket (1..2000 chars)
allowed output: one enum value
success: label exact match + valid format
safety: injection cannot change output set
missing evidence: uncertain
source limits: no user history beyond current ticket
```

Use a stable template renderer. Runtime values must remain data and must be validated
before interpolation. Never assemble prompts by blindly concatenating unknown source text
with trusted SQL, shell, or instructions.

## 6. Prompt engineering versus training

- **Prompt engineering:** change the invocation of an existing model.
- **Instruction tuning:** train a model on many instruction/response examples to follow
  instructions broadly.
- **Fine-tuning:** update weights for a narrower domain/task.
- **Retrieval:** supply current and private facts at runtime.
- **Deterministic rules/code:** handle exact logic, validation, permissions, and limits.

Start with a measured prompt and retrieval, because changing facts should not require
retraining. Consider tuning when repeated benchmarks show that prompting cannot meet a
quality target and data/governance support training.

## 7. Testing prompts as transformations

Partition cases:

| Case class | Purpose |
| --- | --- |
| Normal | Core mapping works |
| Boundary | Distinguish nearby labels |
| Ambiguous | Correct abstention |
| Multilingual/paraphrase | Wording variation |
| Long/truncated | Context and limits |
| Hostile/injection | Data cannot alter policy |
| Empty/malformed | Input validator response |
| Out-of-domain | Stable refusal/escalation |

Keep an authoring/dev set separate from a held-out validation set. If you tune the prompt
on every test, it may look correct by memorizing your test wording.

The offline `prompt_benchmark.py` computes accuracy, abstentions, and estimated tokens.
It shows that adding demonstrations can improve a category synonym while increasing
prompt cost. It is a focused learning mock, not proof of a real model's behavior.

## 8. Cost, latency, and reliability implications

Every few-shot demonstration is included in every call. Ten 100-token examples add 1,000
input tokens to each request:

```text
10,000 calls * 1,000 extra tokens = 10 million extra input tokens
```

System instructions, examples, evidence, and history all compete with the output budget.
Long prompts may add latency and provider input limits. Reliability can improve if
examples resolve ambiguity, but can also decline if they dominate or reveal sensitive
records.

Measure:

```text
quality per case slice
valid-contract rate
abstention calibration
input/output tokens
p50/p95/p99 latency
cost per successful case
safety violations
```

## 9. Failure analysis

| Failure | Likely cause | Debug action |
| --- | --- | --- |
| Correct idea, wrong format | Weak output contract | Use enum/schema and contract validation |
| Same example text always echoed | Overweighting demonstrations | Reduce/directly vary examples and test paraphrases |
| Confident guess on missing context | No abstention path | Add rule, example, and metric |
| Old fact in answer | Parametric memory used instead of retrieval | Supply versioned evidence and reject unsupported values |
| Instructions follow customer text | Trust boundary failure | Separate data, reduce tools, validate downstream output |
| Good demo, poor production score | Prompt overfit or unrepresentative cases | Expand held-out set and slices |

## 10. Step-by-step debugging checklist

1. Render and inspect the exact prompt, excluding/redacting sensitive values in the log.
2. Confirm required instruction, context, examples, and output contract are all present.
3. Verify the request did not exceed/truncate the context budget.
4. Compare the result with one raw expected case and one abstention case.
5. Distinguish semantic error from format error.
6. Re-run on all held-out cases, not only the failed row.
7. Change one instruction/example/category at a time.
8. Check token and latency change before promotion.

## 11. Common misconceptions

- **“A longer prompt is more precise.”** It can dilute key rules and cost more.
- **“Few-shot means include every historical ticket.”** It means a small, representative
  demonstration set.
- **“A persona can enforce authority.”** Authorization is application policy.
- **“JSON in the prompt guarantees JSON.”** Parse and validate every response.
- **“The most polished answer is best.”** Correctness and safety are measured by the task.
- **“Prompt engineering replaces testing.”** It creates a version that requires testing.

## 12. Graded exercises

1. **Rewrite (15):** Turn the vague prompt “summarize this ticket” into a specification
   with goal, audience, source, output, and missing-data behavior.
2. **Examples (15):** Create zero-, one-, and few-shot variants for a three-label task and
   calculate added token cost for 10,000 calls.
3. **Evaluation (20):** Add one normal, boundary, ambiguous, and injection case per label.
4. **Lab (25):** Run `prompt_benchmark.py`. Explain the reported accuracy/abstention and
   why its improvement cannot yet be generalized to a real provider.
5. **Release (25):** Define the held-out promotion threshold, hard safety gates, rollback,
   prompt version, and owner for a production classification prompt.

## 13. LMS demonstration walkthrough

Use `https://lms.snvaveranda.com/mod/resource/view.php?id=8633`. There are
three scenarios rather than one generic prompt lesson:

- **NexAI:** zero-, one-, and few-shot specifications create executive,
  research, business-proposal, legal-case, and market-research documents for
  different audiences.
- **InnovateTech:** a common method is applied to six different contracts:
  summarization, code generation, document-grounded answering, translation,
  classification, and information extraction.
- **TechStream:** a deployment incident describes a bad YAML change, skipped
  integration tests, 503 responses from the user-authentication service for
  45 minutes affecting about 30% of sessions, rollback/patch, and follow-up
  prevention. The vague combined prompt is refined into sentence
  classification, exact extraction, a one-line Slack update, and translation.

Think of this as refining a target table specification. First define the
source fields and transformation; then add required columns, allowed values,
format, missing-data behavior, and a sample row. Zero-shot is enough only for
a clear, well-known task. One-shot establishes a format. Few-shot is useful
when class boundaries or style are difficult, but each example consumes
tokens and can encode bias. For TechStream, expected extracted facts include
the affected service, code, duration, and resolution team; "unknown" is safer
than inventing a fact.

Beginner sequence: copy only the source facts into a case table; write and
run the zero-shot variant; add one representative pair; add boundary examples;
decompose multi-NLP and incident requirements into jobs; evaluate outputs on a
held-out set; and change one ambiguity per revision. Treat answer text as data
that must be parsed, not as proof.

`examples/prompt_benchmark.py` is the safe counterpart for the repository's
original support-ticket case. It is narrower than the LMS business breadth but
tests the same variant/evaluator discipline offline. Practice by creating a
new example in your own words, adding ambiguous and instruction-injection
cases, and requiring accurate abstention. Do not evaluate by copying expected
LMS wording.
