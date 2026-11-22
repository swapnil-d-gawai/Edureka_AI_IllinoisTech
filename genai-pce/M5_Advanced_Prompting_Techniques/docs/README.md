# Module 5: Advanced Prompting Techniques

- **LMS presentation:** https://lms.snvaveranda.com/mod/resource/view.php?id=8634
- **Presentation ID:** `8634`
- **Course:** [Generative AI, Prompting and Context Engineering](https://lms.snvaveranda.com/course/view.php?id=249)

## Deck map

1. Chain-of-thought, tree-of-thought, self-consistency, and least-to-most reasoning
2. Generated knowledge and step-back prompting
3. Adversarial prompts, prompt injection, defenses, and safe fallbacks
4. Prompt selection, optimization, ambiguity, testing, and human review

## Learning objectives

- Select a structured reasoning pattern for the task and risk level.
- Compare multiple hypotheses and aggregate repeated samples carefully.
- Recognize direct and indirect prompt-injection patterns.
- Combine deterministic controls with prompts and human-in-the-loop review.
- Evaluate advanced prompts for accuracy, consistency, safety, cost, and robustness.

> These notes summarize and interpret the presentation for study and practice; they do not reproduce the deck.

## LMS demonstration walkthrough

- **Demonstration resource:** https://lms.snvaveranda.com/mod/resource/view.php?id=8635
- **Actual LMS work:** SmartCart separates compound support complaints and
  branches return-policy decisions; FinSight tests direct injection; TrendHive
  bootstraps and refines review-analysis prompts; sales outreach is stress/
  A-B/cross-model tested; StratNova iterates a client report with human review.
- **Inputs and expected results:** use complaint/policy facts, protected label
  mappings, review lists, noisy sales notes or profile text, and dated
  consulting notes. Expected outputs are structured issue/policy decisions,
  no confidential-label substitution, reusable audience-specific prompts,
  scored robustness results, and an approved client-facing revision with
  reviewer rationale.
- **Beginner workflow:** isolate facts from instructions; ask for a concise
  reasoning plan or explicit decision branches rather than hidden
  chain-of-thought; test official policy and injected text as separate fields;
  generate prompt candidates; score normal, noisy, ambiguous, and adversarial
  cases; then require a human approval gate for external or consequential
  text. Log each revision.
- **Safe/offline counterpart:** `guarded_triage.py` performs deterministic
  hypothesis sampling, injection filtering, and escalation with no provider.
  Its protected incident workflow is the repository's original case, not a
  replacement for the broader LMS businesses.
- **Relationship to the original example:** the exercise supplies the
  controls—separation, schemas, allowlists, aggregation, and HITL—to apply to
  SmartCart, FinSight, TrendHive, sales, and consulting scenarios.
- **Deliberate practice:** add a branch where evidence contradicts a policy
  outcome, then score three prompting strategies on accuracy, disagreement,
  injection resistance, cost, and review burden. A plausible rationale is not
  permission to bypass deterministic policy checks.
