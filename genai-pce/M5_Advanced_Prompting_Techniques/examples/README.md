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

## LMS bridge and optional provider practice

The LMS resource (`8635`) also exercises SmartCart CoT/ToT support, FinSight
prompt-injection defense, TrendHive auto-prompting, sales prompt robustness,
and StratNova human review. The guarded triage code is an offline bridge for
the application-owned checks shared by all five. For optional live work,
replace hypothesis generation behind an adapter, while preserving untrusted
input separation, allowlists, deterministic policy checks, hard escalation,
and human approval. Never use a provider's rationale as authorization.

SQL/Informatica/Unix are familiar mental models, not limits on the LMS's
customer, finance, marketing, sales, or consulting scenarios.
