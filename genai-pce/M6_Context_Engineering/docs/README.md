# Module 6: Context Engineering

- **LMS presentation:** https://lms.snvaveranda.com/mod/resource/view.php?id=8636
- **Presentation ID:** `8636`
- **Course:** [Generative AI, Prompting and Context Engineering](https://lms.snvaveranda.com/course/view.php?id=249)

## Deck map

1. Task, domain, interaction, placement, ordering, and granularity of context
2. Context windows, token costs, truncation, and context-growth trade-offs
3. Chunking, summarization, windowing, checkpointers, stores, and conversation memory
4. Document ingestion, retrieval, multi-turn history, and token optimization

## Learning objectives

- Select context for a task rather than indiscriminately filling the window.
- Distinguish buffer, summary, thread-level, and user-level memory.
- Build retrieval-friendly chunks with source metadata.
- Combine retrieval, summaries, and recent turns without losing evidence.
- Measure token use and test privacy, relevance, and recency trade-offs.

> These notes summarize and interpret the presentation for study and practice; they do not reproduce the deck.

## LMS demonstration walkthrough

- **Demonstration resource:** https://lms.snvaveranda.com/mod/resource/view.php?id=8637
- **Actual LMS work:** ShopEase builds recent-buffer plus summary memory;
  compares ungrounded and retrieval-grounded support replies; chunks and
  map-reduces a policy handbook; and compares full-history, sliding-window,
  and buffer-summary token use.
- **Inputs and expected results:** ordered conversations, policy chunks with
  source metadata, long policy text, and model/token settings feed each demo.
  Expected evidence is retained recent turns plus a compact summary,
  source-cited answers, overlapping chunk summaries plus a final synthesis,
  and a per-turn prompt-token comparison with the trade-off documented.
- **Beginner workflow:** set a small buffer limit; verify what is kept,
  summarized, or discarded; chunk with stable source IDs; retrieve and enforce
  tenant/topic filters before prompting; map summaries to independent chunks;
  reduce them; then instrument approximate and provider-reported usage. Inspect
  evidence loss on every compaction.
- **Safe/offline counterpart:** `context_engine.py` uses embedded synthetic
  policy text, lexical retrieval, rolling memory, and a mock answer. There is
  no Groq key or source-document upload, while filters and citation IDs remain
  application-enforced.
- **Relationship to the original example:** the repository's local policy
  retrieval is a smaller analogue of ShopEase; metadata isolation and
  evidence IDs transfer directly, but it does not claim to measure a hosted
  model's real usage.
- **Deliberate practice:** reduce the buffer by one turn and identify which
  fact survives only in the summary, then shrink chunks until recall changes.
  Keep a table of context tokens, answer quality, citation correctness, and
  privacy failures.
