# Module 8 exercise: signature-driven prompt optimizer

`prompt_optimizer.py` is an offline DSPy-inspired optimizer. It defines typed examples and a task signature, evaluates several instruction variants on development data, and promotes a version only when it also passes an untouched held-out suite and hard safety gates.

## Run

```bash
cd genai-pce/M8_Prompt_Optimization_Evaluation_DSPy/examples
python prompt_optimizer.py
```

The standard-library implementation uses no model API. A `TaskProgram` interface makes it possible to test real providers or DSPy modules without changing the evaluation harness.

## Extensions

- Connect an optional DSPy program while preserving the same metric interface.
- Add bootstrap few-shot selection and instruction search.
- Measure confidence intervals, subgroup quality, latency, and token cost.
- Add a persisted version manifest and signed approval for promotion.

## LMS bridge and optional provider practice

The LMS resource (`8641`) demonstrates DSPy signatures/modules, ShopEase
`BootstrapFewShot` optimization, and multiple reply metrics. This offline
optimizer provides typed task, split, metric, and promotion-gate practice
before a real DSPy `TaskProgram` is introduced. For optional provider-backed
DSPy work, pass configuration from the environment, keep an offline baseline,
version demonstrations/settings, and require held-out and hard-gate results
before promotion. Never commit LMS examples, compiled artifacts, or keys.

The learner's SQL/Informatica/Unix background offers pipeline analogies but
does not bound the actual DSPy pipeline, optimization, or evaluation scope.
