# Module 5 exercise: guarded hypothesis triage

`guarded_triage.py` models an incident workflow using multiple sampled reasoning paths. It filters suspicious input, validates structured hypotheses, aggregates decisions, detects disagreement, and forces escalation for risky or unresolved cases.

## Run

```bash
cd genai-pce/M5_Advanced_Prompting_Techniques/examples
python guarded_triage.py
```

The exercise is offline. It runs through a deterministic mock model, demonstrates self-consistency, and blocks a simulated prompt-injection attempt before any tool request can be considered.

## Extensions

- Replace keyword hypothesis generation with an optional provider adapter.
- Add a true tool-allowlist and verify every proposed action against it.
- Record calibration curves for confidence and correctness.
- Compare chain, tree, and least-to-most costs on the same held-out cases.
