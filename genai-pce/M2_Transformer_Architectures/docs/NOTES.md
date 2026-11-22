# Module 2 Notes: Transformer Architectures and How LLMs Work

## 1. Prerequisite mental model

Module 1 treated the model as a service. Module 2 opens the service just enough to
understand its behavior. You do not need calculus or ML vocabulary to follow the main
ideas.

A transformer is a repeated set of numeric operations that produces a context-aware
representation for each token, then uses that representation to classify, transform,
or generate text. **Attention** is a mechanism for mixing information from selected
tokens. It does not mean the model is consciously paying attention.

## 2. Why the transformer replaced recurrent assumptions

A recurrent model processes tokens mostly one after another. Distant information must
travel through many steps, which creates training and memory problems. A transformer can
process positions in parallel and calculate relationships between many positions in a
call.

ETL analogy:

- Recurrent processing resembles a row-sequential dependency in which late work waits
  for earlier state.
- Self-attention resembles a controlled many-to-many join over the tokens in one
  bounded stage.
- The context window is the number of rows available for that stage.

The parallel relationship has a cost: ordinary attention compares all positions to all
others, so its time and memory concern grows roughly as \(n^2\) for `n` tokens.

## 3. Q, K, V, and attention in plain language

For every token, the model creates three vectors:

| Vector | Question it helps answer | Analogy |
| --- | --- | --- |
| Query (Q) | “What information is this position looking for?” | Join/select criteria |
| Key (K) | “What kind of information does that other position offer?” | Indexed metadata |
| Value (V) | “What content should be mixed into the result?” | Payload field |

For each query token:

1. Take its dot product with every key.
2. Scale by `1 / sqrt(key_dimension)` to keep scores in a useful numeric range.
3. If generating left-to-right, mask future positions.
4. Apply softmax so weights are nonnegative and sum to one.
5. Multiply every value by its weight and sum the result.

```text
scores = Q dot K / sqrt(d)
weights = softmax(mask(scores))
output = weights dot V
```

A softmax weight is a relative mixture coefficient, not a calibrated probability that a
fact is true and not a complete explanation of the final answer.

## 4. Small numeric example

Assume one query and two keys:

```text
query = [1, 0]
key A = [1, 0]   -> raw score 1
key B = [0, 1]   -> raw score 0
```

With key dimension 2, scaled scores are `0.707` and `0`. Softmax gives approximately
`0.67` and `0.33`. If their values are `A=[10, 0]` and `B=[0, 2]`, the output is:

```text
0.67*[10,0] + 0.33*[0,2] = [6.7, 0.66]
```

Rounding can vary. The important checks are:

- weights sum to approximately 1.0;
- the output is a weighted mixture of values;
- changing the dimension or key values changes the result.

Run `examples/attention_lab.py` to trace the same idea over four positions.

## 5. Causal versus bidirectional attention

**Bidirectional encoder attention** may relate a token to positions on both sides. It is
useful for understanding a complete document, like a join after all source rows are
available.

**Causal decoder attention** sets future positions to an effective negative infinity
before softmax. Position 3 may use positions 1–3, but not 4. This preserves the
left-to-right generation rule:

```text
The job failed   -> the next token is predicted
The job failed d -> the next token is predicted
```

Allowing future tokens would be target leakage—the ML equivalent of a transformation
using a field populated later in the target load.

## 6. A transformer block

A typical block combines:

1. attention;
2. a residual (shortcut) connection;
3. normalization;
4. a feed-forward transformation on each position;
5. another residual connection and normalization.

“Head” means a separate attention projection. Multi-head attention can learn several
different relationship patterns in parallel, then combine them. “Layers” are blocks
stacked one after another. Layer count and hidden dimension contribute strongly to model
size, compute, memory, and latency.

## 7. Architecture selection

| Task shape | Likely family | Reason |
| --- | --- | --- |
| Map incident text to one risk label | Encoder-only | Full input is available; one finite label is produced |
| Translate approved English to French | Encoder-decoder | Source-to-target transformation |
| Draft an investigation response | Decoder-only | Open-ended continuation/generation |
| Extract fields from one document | Encoder or decoder, benchmarked | Task may fit both depending on model and contract |

Never select a family from branding alone. Build a fixed evaluation set and measure
quality, validity, latency, token cost, and memory.

## 8. Tokens, parameters, and token budget

These quantities are unrelated:

- **tokens:** discrete input/output units in a call;
- **embedding dimension:** length of a token's numeric vector;
- **model parameters:** learned weights, often billions;
- **context length:** maximum tokens available to a call;
- **batch size:** how many requests are processed together;
- **KV cache:** stored key/value state reused during generation.

A one-time request with 20,000 input tokens asks the attention/serving stack to work on
far more than a four-word prompt. Output generation then has different behavior because
the model predicts one token at a time, usually reusing cached key/value information.

Example budget:

```text
system 400 + history 1,200 + evidence 4,000 + reserved answer 1,000
= 6,600 tokens
```

There must also be margin for tool results and provider-specific overhead. A sum below
the published limit is not a quality guarantee: old or central evidence can still be
lost to truncation or poor placement.

## 9. Generation walkthrough

At each step, the decoder creates a vocabulary distribution. Decoding then chooses:

```text
next-token candidates: " network" 45%, " application" 30%, " database" 20%, other 5%
```

- **Greedy** chooses “network.”
- **Sampling** may choose a lower-scored candidate.
- **Beam search** keeps several candidate sequences, trading compute for broader search.

The percentages illustrate decoder scores, not a guarantee of truth.

## 10. Serving optimizations and implications

| Technique | Intended benefit | Trade-off/risk |
| --- | --- | --- |
| Quantization | Lower memory and possibly faster/cheaper serving | Numeric precision loss can alter behavior |
| GQA (grouped-query attention) | Less KV memory and bandwidth | Architecture/training choice; verify task quality |
| FlashAttention | More memory-efficient attention calculation | Hardware/software compatibility; optimized but still \(n^2\)-related |
| KV caching | Avoid recomputing past K/V states during generation | Memory grows with active sequence length/concurrency |
| Mixture-of-experts routing | Use a subset of parameters per token | Routing complexity, load imbalance, memory footprint |
| Small language model (SLM) | Lower cost/latency and local deployment | May fail broader reasoning or rare cases |

Optimization is a release decision. Benchmark before and after; compare exact failures,
not only aggregate accuracy.

## 11. Worked architecture and cost case

```text
Task A: categorize 2 million daily log summaries into 6 fixed control risks
Task B: answer 2,000 analyst questions over 300 pages of policy
```

Task A favors an encoder/classifier with batch processing. Task B may favor a routed
retrieval + generation design. Running the largest decoder for Task A could multiply
token cost and p95 latency without improving the six-way classification.

Track:

```text
valid outputs / total
task error by class and segment
input/output tokens per record
p50, p95, p99 latency
memory/accelerator utilization
cost per 1,000 successful jobs
```

## 12. Failure analysis and debugging

| Observation | Check |
| --- | --- |
| Output ignores early instruction | Context truncation, placement, competing text, model behavior |
| Attention rows do not sum to one in the lab | Softmax implementation or dimension shape |
| Causal output uses a future position | Mask applied after or incorrectly indexed |
| Latency rises sharply with long inputs | Quadratic attention, staging, queueing, output length |
| Small model performs worse after quantization | Re-run fixed tests and check precision/runtime path |
| Batch succeeds offline but stalls in production | Memory, concurrency, queue, timeout, accelerator saturation |

Debug checklist:

1. Print tensor/vector dimensions (or small matrix shapes) before scores.
2. Confirm the scale is based on key dimension.
3. Confirm causal masking occurs before softmax.
4. Check every attention row sums to approximately one.
5. Compare fixed seed/greedy output on identical model and settings.
6. Reconcile tokenizer count with provider-reported input and output tokens.
7. Test truncation, concurrency, and timeout behavior separately.

## 13. Common misconceptions

- **“Attention shows the reason.”** It shows one internal mixture, not an audit trail.
- **“Longer context means better retrieval.”** Irrelevant content can distract and costs more.
- **“Parameters equal context tokens.”** They measure model weights versus per-call content.
- **“Softmax means truth probability.”** It normalizes scores at a prediction step.
- **“Encoder-decoder is always best for summarization.”** Modern decoder-only models can work; benchmark.
- **“GPU use is only a training concern.”** Inference memory and throughput are operations concerns.

## 14. Graded exercises

1. **Mechanics (15):** Compute a two-token Q/K softmax and explain every term.
2. **Leak prevention (15):** Mark allowed and masked positions for a four-token causal row.
3. **Selection (20):** Recommend a family for classification, translation, and drafting; state the evidence needed to overturn each choice.
4. **Lab (20):** Add assertions to a local copy of `attention_lab.py` that every output shape is expected and every attention concept is row-normalized.
5. **Operations (30):** Design benchmark slices for 256, 2K, and 16K tokens. Include quality,
   p95, memory, and cost, and explain one safe failure at the context limit.

## 15. LMS demonstration walkthrough

Use `https://lms.snvaveranda.com/mod/resource/view.php?id=8629` for the
ShopEase activity. The three demonstrations are one learning sequence:

1. **Attention inspection:** input one support sentence; tokenize it; run a
   BERT encoder with attention available; select a layer and head; and inspect
   both one matrix and a layer average. Expected artifacts are token IDs/text,
   attention tensor dimensions, heatmaps, and strongest-attended tokens for a
   selected query.
2. **Architecture comparison:** pass related work to BERT (a missing-word
   prediction), GPT-2 (left-to-right continuation), and T5 (conditioned
   transformation). The expected outputs differ by architecture and should not
   be ranked without a common task rubric.
3. **Token/context limits:** tokenize the same product/support text with
   WordPiece, BPE, and SentencePiece variants. Record token counts, special
   tokens, truncation, and the warning behavior at a configured maximum.

Begin with the SQL/ETL analogy: query and key scores resemble a matching join,
softmax is a per-row normalization, and each transformer layer is another
mapping in a scheduled chain. Causal masking is an access rule: later columns
are unavailable to earlier tokens. Unlike a SQL row, however, attention
weights are learned signals and do not prove semantic truth.

The offline `attention_lab.py` is the default counterpart. It exposes the
numeric mechanics, causal mask, family selection, and token-budget estimate
without downloads. The original four-token ShopEase-like example is intentionally
smaller than the LMS's pretrained models so a beginner can audit every
calculation. Optional real-model work should first download only public model
artifacts through an approved environment; never commit caches.

For deliberate practice, hand-compute one two-token or four-token attention
row, alter one query, and predict the ranking before execution. Then compare
one sentence across tokenizers and prepare an operations note explaining why
the same word count can lead to different token cost and context failures.
