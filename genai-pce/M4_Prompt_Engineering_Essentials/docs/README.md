# Module 4: Prompt Engineering Essentials

- **LMS presentation:** https://lms.snvaveranda.com/mod/resource/view.php?id=8632
- **Presentation ID:** `8632`
- **Course:** [Generative AI, Prompting and Context Engineering](https://lms.snvaveranda.com/course/view.php?id=249)

## Deck map

1. Prompt purpose, components, personas, constraints, and output indicators
2. Zero-, one-, and few-shot techniques and prompt templates
3. Instruction tuning, testing, debugging, and NLP task patterns
4. Prompt variants, evaluation, pitfalls, and iterative refinement

## Learning objectives

- Construct prompts with a clear goal, context, constraints, and output contract.
- Select an appropriate zero-, one-, or few-shot pattern.
- Use reusable role, chat, and history-aware templates without prompt ambiguity.
- Test prompt variants against normal, edge, and adversarial cases.
- Distinguish prompt engineering, fine-tuning, and instruction tuning.

> These notes summarize and interpret the presentation for study and practice; they do not reproduce the deck.

## LMS demonstration walkthrough

- **Demonstration resource:** https://lms.snvaveranda.com/mod/resource/view.php?id=8633
- **Actual LMS work:** NexAI drafts executive/research/business/legal/market
  documents with zero-, one-, and few-shot prompts; InnovateTech designs
  prompts for six NLP tasks; TechStream iteratively debugs a CI/CD incident
  prompt.
- **Inputs and expected results:** inputs are a brief plus optional examples, or
  TechStream's YAML-caused deployment incident. Expected records include the
  requested document shape; summary/code/answer/translation/classification/
  extraction; and the incident's affected service, HTTP `503`, 45-minute
  duration, SRE ownership, Slack summary, and a Spanish rendering of the
  resolution sentence.
- **Beginner workflow:** write an explicit goal/output schema first; run it
  with no example, one format example, then a few representative examples;
  score facts and format separately; for the incident, decompose the vague
  prompt into classify, extract, summarize, and translate jobs; repair one
  ambiguity per iteration and rerun held-out cases.
- **Safe/offline counterpart:** use `prompt_benchmark.py` with its labeled mock
  corpus. It represents the original repository support use case and exposes
  the same zero/one/few-shot comparison without depending on generated LMS
  answers.
- **Relationship to the original example:** ticket classification is narrower
  than NexAI's document breadth and InnovateTech's six tasks, but gives the
  same testable contract for variants, labels, abstention, and cost.
- **Deliberate practice:** create an input/output example that teaches
  structure without leaking a copied answer, then add a missing-field edge
  case and an adversarial instruction. Require the evaluator—not the
  prose—to decide which prompt variant is promotable.
