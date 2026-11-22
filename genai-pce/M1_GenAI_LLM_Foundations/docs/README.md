# Module 1: Generative AI and LLM Foundations

- **LMS presentation:** https://lms.snvaveranda.com/mod/resource/view.php?id=8626
- **Presentation ID:** `8626`
- **Course:** [Generative AI, Prompting and Context Engineering](https://lms.snvaveranda.com/course/view.php?id=249)

## Deck map

1. Generative versus discriminative AI and major generative model families
2. Tokens, embeddings, probability, decoding, and transformer model patterns
3. Pretraining, fine-tuning, alignment, evaluation, and lifecycle management
4. Proprietary/open models, tooling, use-case fit, and responsible AI

## Learning objectives

- Distinguish generation, classification, and rule-based automation.
- Explain tokens, embeddings, attention, and next-token generation at a conceptual level.
- Compare BERT, GPT, and T5 patterns and identify suitable tasks for each.
- Describe an LLM development and deployment lifecycle.
- Apply basic bias, safety, transparency, and monitoring controls.

> These notes summarize and interpret the presentation for study and practice; they do not reproduce the deck.

## LMS demonstration walkthrough

- **Demonstration resource:** https://lms.snvaveranda.com/mod/resource/view.php?id=8627
- **Actual LMS work:** RetailVerse trains a small PyTorch transformer to classify
  customer reviews as `negative`, `neutral`, or `positive`; a second activity
  uses Eventora marketing briefs to compare Gemini generation settings.
- **Inputs and expected results:** the RetailVerse CSV has `review` and
  `sentiment` columns. Tokenization, a 15-token encoder path, train/validation
  loops, and an inference function should produce the three named labels (for
  example, praise → positive and a short complaint → negative). Eventora
  supplies event type/audience/tone plus temperature, top-p, and output-token
  controls; the observable result is a promotional paragraph whose creativity
  and length track those controls.
- **Beginner workflow:** (1) validate the CSV columns and label set, (2) map
  whitespace tokens and labels to IDs, (3) add special/padding tokens, (4)
  explain embedding, position, attention, and feed-forward stages as mapping
  transformations, (5) train and inspect loss, (6) predict a few unseen reviews,
  and (7) compare low- versus high-randomness Eventora copy using identical
  prompts and a manual length/tone rubric.
- **Safe/offline counterpart:** use `examples/support_intake.py`; it substitutes
  local rules and a mock generator while retaining schema, validation, and
  approval stages. Do not upload the LMS CSV or place provider credentials in
  the repository.
- **Relationship to the original example:** both are intake-to-decision
  pipelines. The original is a simpler support-routing analogue; it does not
  claim to reproduce RetailVerse model training or Eventora's hosted output.
- **Deliberate practice:** add one unseen review per label, record predicted
  labels and confidence, then repeat the copy exercise with fixed wording and
  only one generation control changed at a time. Compare accuracy, useful
  abstention, and tone consistency.
