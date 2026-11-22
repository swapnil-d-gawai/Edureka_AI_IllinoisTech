# Module 7: Structured Outputs, Function Calling and Tool Use

- **LMS presentation:** https://lms.snvaveranda.com/mod/resource/view.php?id=8638
- **Presentation ID:** `8638`
- **Course:** [Generative AI, Prompting and Context Engineering](https://lms.snvaveranda.com/course/view.php?id=249)

## Deck map

1. JSON mode, response schemas, and typed data extraction
2. Validation, malformed output, retries, and fallback paths
3. Function/tool definitions, routing, and model-to-application round trips
4. Safe schemas, least privilege, auditability, and production controls

## Learning objectives

- Define machine-consumable response and tool contracts.
- Parse and validate model output as untrusted input.
- Route tool intent without granting the model direct execution authority.
- Constrain tools with narrow types, ranges, enums, and approval rules.
- Implement controlled repair, retry, refusal, and human escalation.

> These notes summarize and interpret the presentation for study and practice; they do not reproduce the deck.

## LMS demonstration walkthrough

- **Demonstration resource:** https://lms.snvaveranda.com/mod/resource/view.php?id=8639
- **Actual LMS work:** AsterOne converts free-text IT incidents to validated
  JSON through prompt-only and schema-enforced paths; TechAssist repairs
  wrapped, malformed, wrong-type, missing, or truncated output locally and
  escalates only unrecoverable meaning.
- **Inputs and expected results:** source messages contain requester,
  department, asset, symptom, urgency, and impact. The target is one
  predictable incident object; Pydantic/local checks reject wrong types,
  strip safe wrappers, repair only safe syntax, and identify incomplete
  semantics. The LMS output is valid JSON or a controlled human-review result,
  never invented missing facts.
- **Beginner workflow:** write the smallest useful Pydantic schema; parse an
  untrusted response; validate; separate deterministic cleanup from semantic
  completion; retry with actionable field errors and a budget; then route the
  validated object into a read-only mock operation. Save the raw result and
  validation trace for debugging without retaining secrets.
- **Safe/offline counterpart:** `structured_router.py` performs explicit
  standard-library validation and a malformed-response retry before
  dispatching a fixed mock tool. Optional Pydantic practice can mirror the LMS
  without adding the hosted Groq dependency.
- **Relationship to the original example:** the original incident schema and
  authorization boundary are the same learning pattern as AsterOne/TechAssist,
  with a deliberately smaller field set and no real ticket side effects.
- **Deliberate practice:** inject Markdown fencing, a trailing comma, a string
  where a number is required, an omitted field, and truncated severity. Mark
  which cases are locally safe to repair and which must abstain/escalate.
