# Module 8: Prompt Optimization, Evaluation and DSPy

- **LMS presentation:** https://lms.snvaveranda.com/mod/resource/view.php?id=8640
- **Presentation ID:** `8640`
- **Course:** [Generative AI, Prompting and Context Engineering](https://lms.snvaveranda.com/course/view.php?id=249)

## Deck map

1. DSPy signatures, modules, `Predict`, `ChainOfThought`, and `ReAct`
2. Few-shot bootstrapping, MIPRO, compilation, and validation
3. Metrics, multiple-model routing, and self-improving pipelines
4. Deployment, versioning, rollback, and manual-prompting trade-offs

## Learning objectives

- Express an AI task as typed inputs, outputs, and a reusable program.
- Compare direct, reasoning, and tool-using module patterns.
- Define metrics that represent correctness and operational constraints.
- Optimize on training data and decide promotions on held-out data.
- Version compiled programs and monitor cost, quality, drift, and safety.

> These notes summarize and interpret the presentation for study and practice; they do not reproduce the deck.

## LMS demonstration walkthrough

- **Demonstration resource:** https://lms.snvaveranda.com/mod/resource/view.php?id=8641
- **Actual LMS work:** ShopEase defines DSPy signatures and a triage/reply
  pipeline, compiles a zero-shot classifier with `BootstrapFewShot`, and
  evaluates a reply program with fact, concision, model-judged groundedness,
  relevance, and weighted composite metrics.
- **Inputs and expected results:** typed support-ticket fields plus training,
  labeled development, and policy-question examples produce category/urgency,
  a drafted reply, selected few-shot demonstrations, baseline-versus-compiled
  accuracy, and metric/component scores on one common evaluation set. A
  promotion requires objective improvement and no hard-gate regression.
- **Beginner workflow:** define typed task inputs/outputs; run direct and
  chain-of-thought modules; establish a zero-shot baseline; split train/dev/
  untouched holdout data; compile only from training examples; compute exact
  match and independent quality/safety metrics; compare; and version the
  selected program, data, and settings before promotion.
- **Safe/offline counterpart:** `prompt_optimizer.py` uses a DSPy-inspired
  signature and deterministic candidates. It exercises the same split and
  held-out promotion gate without a Groq/DSPy installation; provider-backed
  practice remains optional.
- **Relationship to the original example:** the repository optimizer is a
  minimal teaching substitute for the full DSPy workflow. It preserves typed
  boundaries, metric direction, versioning, and safety gates rather than
  reproducing LMS code or compiled demonstrations.
- **Deliberate practice:** create one metric that can be gamed and pair it
  with a fact-grounding gate; then inspect a candidate that improves the
  composite but regresses a protected subgroup or safety check. It must not
  promote merely because its average rose.
