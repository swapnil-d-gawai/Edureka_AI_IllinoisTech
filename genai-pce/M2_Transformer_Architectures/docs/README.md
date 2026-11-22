# Module 2: Transformer Architectures and How LLMs Work

- **LMS presentation:** https://lms.snvaveranda.com/mod/resource/view.php?id=8628
- **Presentation ID:** `8628`
- **Course:** [Generative AI, Prompting and Context Engineering](https://lms.snvaveranda.com/course/view.php?id=249)

## Deck map

1. RNN limitations and the purpose of self-attention
2. Queries, keys, values, multi-head attention, and architecture families
3. Pretraining, fine-tuning, alignment, tokenization, and generation
4. GQA, FlashAttention, mixture-of-experts, and small-model selection

## Learning objectives

- Explain why attention improves parallel, context-aware sequence processing.
- Trace scaled dot-product attention and causal masking.
- Choose encoder-only, decoder-only, or encoder-decoder architectures.
- Relate token budgets and next-token prediction to serving behavior.
- Compare latency and memory optimizations with model-size trade-offs.

> These notes summarize and interpret the presentation for study and practice; they do not reproduce the deck.

## LMS demonstration walkthrough

- **Demonstration resource:** https://lms.snvaveranda.com/mod/resource/view.php?id=8629
- **Actual LMS work:** ShopEase visualizes BERT self-attention, compares BERT,
  GPT-2, and T5 behaviors, and compares WordPiece, byte-pair, and SentencePiece
  tokenization near context-window boundaries.
- **Inputs and expected results:** input is customer-support or product text.
  Record its token sequence, selected layer/head, attention-matrix shape, the
  strongest links, a fill-mask result (BERT), continuation (GPT-2), conditioned
  generation (T5), token counts, and truncation/length status. A sentence can
  have the same word count in each model but a different token count.
- **Beginner workflow:** tokenize once; inspect special and subword tokens; run
  the attention forward pass; draw one head and a layer average; switch only
  layer/head or architecture and compare; then repeat with long and unknown
  vocabulary and inspect the context-limit warning. Relate query/key/value
  matching to SQL joins and the repeated layer stack to a mapping chain.
- **Safe/offline counterpart:** run `attention_lab.py`, whose small numeric
  matrices expose causal masking, normalization, architecture selection, and
  an estimated budget without downloading a model. Real pretrained-tokenizer
  and heatmap work is optional after local caching is understood.
- **Relationship to the original example:** the lab is the arithmetic core of
  the LMS activity, deliberately reduced from pretrained 12-layer BERT to a
  four-token example for traceability.
- **Deliberate practice:** hand-calculate one attention row, change one query
  vector, predict which attention weight should rise, and then verify it;
  repeat the same shop message with two tokenization strategies and explain
  the budget difference in an operations handoff.
