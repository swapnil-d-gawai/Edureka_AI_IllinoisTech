# Module 2 exercise: auditable attention lab

`attention_lab.py` implements a dependency-free, numerically transparent self-attention calculation. It validates vectors, supports a causal mask, normalizes attention rows, identifies a suitable transformer family, and estimates a simple token budget.

## Run

```bash
cd genai-pce/M2_Transformer_Architectures/examples
python attention_lab.py
```

The output contains attention weights for an illustrative four-token review, their row sums, a mask demonstration, and architecture recommendations. No packages, model downloads, keys, or paid services are used.

## Extensions

- Add multi-head attention and concatenate the head outputs.
- Compare `O(n²)` attention materialization with a blocked implementation.
- Add positional encodings and a residual/feed-forward block.
- Load a real tokenizer behind an optional interface and compare actual token counts.

## LMS bridge and optional provider practice

The LMS resource (`8629`) asks learners to inspect ShopEase BERT attention,
compare BERT/GPT-2/T5 architecture behavior, and compare tokenizer/context
limits. This example is the offline numeric bridge: verify the weights and
masking before optionally loading public model/tokenizer artifacts behind
isolated adapters. A first external-model run may need downloads; cached
artifacts, credentials, and downloaded model files must remain outside the
repository.

SQL, Informatica, and Unix analogies explain mechanics for a pipeline learner;
they do not restrict the actual transformer families, visualizations, or
context-limit experiments demonstrated in the LMS.
