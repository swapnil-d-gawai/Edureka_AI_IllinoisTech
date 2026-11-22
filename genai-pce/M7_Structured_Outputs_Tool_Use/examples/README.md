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
