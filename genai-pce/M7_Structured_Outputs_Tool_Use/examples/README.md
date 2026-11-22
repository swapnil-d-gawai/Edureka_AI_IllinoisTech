# Module 7 exercise: structured incident tool router

`structured_router.py` parses a simulated model response, validates a typed incident schema, and dispatches one read-only tool from a fixed registry. It demonstrates a malformed-response retry and refuses unknown or consequential operations.

## Run

```bash
cd genai-pce/M7_Structured_Outputs_Tool_Use/examples
python structured_router.py
```

The default mock is deterministic and entirely offline. A real provider can be added behind `RawModel`, but all schema and tool authorization checks remain application-owned.

## Extensions

- Add optional Pydantic models and compare their errors with the explicit standard-library validator.
- Add role-based authorization and idempotency to the tool registry.
- Introduce a state-changing tool requiring signed human approval.
- Add a retry budget that returns the validation feedback to the mock or real model.

## LMS bridge and optional provider practice

The LMS resource (`8639`) uses AsterOne incident JSON/Pydantic validation and
TechAssist staged malformed-output recovery. This router is an offline
standard-library counterpart. An optional real `RawModel` may be added for
schema-enforced responses, but Pydantic/application validation, raw-response
preservation, retry limits, safe syntax repair, and tool allowlists remain
mandatory. Missing semantics must produce review/abstention rather than
fabrication.

SQL staging-table and Informatica validation analogies support learning; they
do not narrow the LMS service-desk extraction and recovery breadth.
