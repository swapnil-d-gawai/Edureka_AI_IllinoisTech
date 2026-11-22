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

## LMS bridge and optional provider practice

The LMS demonstration (`docs/README.md`, resource `8627`) covers RetailVerse
review classification with a small transformer and Eventora creative-copy
generation. Run this support-intake mock first to learn validation and routing;
then, only as an extension, add a provider adapter for the Eventora task or a
locally approved transformer. Keep keys in environment configuration and
compare outputs against a fact/tone/length rubric. The default remains fully
offline and does not include the LMS dataset or generated LMS solutions.

SQL, Informatica, and Unix experience is pedagogical context for understanding
the pipeline; it is not a limit on the breadth of the RetailVerse/Eventora
demonstrations or on learner practice.
