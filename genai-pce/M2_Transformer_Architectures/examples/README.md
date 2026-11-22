# Module 2 exercise: auditable attention lab

`attention_lab.py` implements a dependency-free, numerically transparent self-attention calculation. It validates numeric vectors, supports a causal mask, normalizes attention rows internally, identifies a suitable transformer family, and estimates a simple token budget.

## Run

```bash
cd genai-pce/M2_Transformer_Architectures/examples
python attention_lab.py
```

The four rows of input are illustrative numeric vectors, not a tokenized review.
For each query row, the script computes a 4-entry attention-weight row
`A_i = softmax((Q_i Kᵀ) / sqrt(d_k))` and multiplies it by `V`. The printed
bidirectional and causal results are therefore **4×2 attention-weighted value
mixtures**, `Y = A V`, not the 4×4 attention matrix `A`.

Each attention row `A_i` is normalized to sum to 1 (with future weights set to
zero in causal mode), but rows of the printed value mixtures need not sum to 1.
The script currently does not print `A` or its row sums, so use the displayed
mixtures to inspect value aggregation, not attention normalization. A learner
who instruments `self_attention()` can separately print `attention` and
`sum(attention)` immediately after each softmax call. The remaining output shows
a causal calculation, architecture recommendations, and a shared token
budget. No packages, model downloads, keys, or paid services are used.

## Extensions

- Add multi-head attention and concatenate the head outputs.
- Compare `O(n²)` attention materialization with a blocked implementation.
- Add positional encodings and a residual/feed-forward block.
- Load a real tokenizer behind an optional interface and compare actual token counts.

## LMS bridge and optional provider practice

The LMS resource (`8629`) asks learners to inspect ShopEase BERT attention,
compare BERT/GPT-2/T5 architecture behavior, and compare tokenizer/context
limits. This example is the offline numeric bridge: inspect the weighted value
aggregation and, if desired, expose the internal weights and verify those rows
sum to 1 before optionally loading public model/tokenizer artifacts behind
isolated adapters. A first external-model run may need downloads; cached
artifacts, credentials, and downloaded model files must remain outside the
repository.

SQL, Informatica, and Unix analogies explain mechanics for a pipeline learner;
they do not restrict the actual transformer families, visualizations, or
context-limit experiments demonstrated in the LMS.
