# Module 1 exercise: support-intake design

`support_intake.py` simulates an offline customer-support intake pipeline. It validates ticket inputs, uses a small rule-based classifier, drafts a response through a mock model interface, and applies policy checks before producing an action.

## Run

Requires Python 3.10+ and only the standard library:

```bash
cd genai-pce/M1_GenAI_LLM_Foundations/examples
python support_intake.py
```

The default run prints structured decisions for refund, shipment, and ambiguous tickets. One ticket is escalated because its policy check cannot be resolved. The model is deliberately mocked; there are no API credentials or network calls.

## Extensions

- Replace keyword classification with a validated local or hosted model while retaining the approval gate.
- Add segment-level evaluation and a confusion matrix.
- Create a benchmark containing multilingual and adversarial tickets.
- Add a `Provider` implementation for a real API behind an explicit configuration object.
