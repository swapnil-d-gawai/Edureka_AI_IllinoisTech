# Module 4 exercise: prompt variant benchmark

`prompt_benchmark.py` builds zero-, one-, and few-shot prompt variants for support-ticket classification and evaluates them against a labeled corpus through a deterministic mock model. It validates the prompt specification and reports accuracy, abstention rate, and prompt cost.

## Run

```bash
cd genai-pce/M4_Prompt_Engineering_Essentials/examples
python prompt_benchmark.py
```

The default run demonstrates why examples can improve a narrowly scoped format while still failing if ambiguous cases are underrepresented. It is fully offline and uses no provider credentials.

## Extensions

- Add a held-out benchmark and compare exact labels by customer segment.
- Score calibration: reward correct abstention for insufficient evidence.
- Add prompt-injection test messages and assert they cannot change the label set.
- Isolate a real provider behind `PromptModel` and keep the same deterministic evaluator.

## LMS bridge and optional provider practice

The LMS resource (`8633`) spans NexAI business documents, InnovateTech's six
NLP task types, and TechStream's incident-prompt debugging—not only support
classification. Use this labeled benchmark first for zero/one/few-shot
discipline, then adapt the input/output cases to another scenario. A provider
can optionally implement `PromptModel`; the evaluator, held-out cases, safety
tests, and abstention policy must remain unchanged and provider access must be
environment-configured and opt-in.

SQL/Informatica/Unix experience is pedagogical context for inputs, mapping,
control flow, and validation; it is not a boundary on the LMS's document and
NLP demonstration breadth.
