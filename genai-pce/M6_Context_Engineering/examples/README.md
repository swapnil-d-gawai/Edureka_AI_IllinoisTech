# Module 6 exercise: local policy retrieval and memory

`context_engine.py` implements an offline document chunker, metadata-constrained lexical retriever, rolling conversation window, and structured memory store. It validates tenant and jurisdiction filters, preserves source IDs, and produces a grounded mock answer.

## Run

```bash
cd genai-pce/M6_Context_Engineering/examples
python context_engine.py
```

The standard library-only example loads embedded policy text, retrieves the relevant effective document for one tenant, and demonstrates that a different tenant cannot receive that evidence.

## Extensions

- Add an embedding index behind the retriever interface.
- Compare overlap sizes on retrieval recall and token cost.
- Add document expiry, supersession, and stale-source detection.
- Persist redacted memory to an encrypted local store and implement user deletion.

## LMS bridge and optional provider practice

The LMS resource (`8637`) uses ShopEase buffer-plus-summary memory, retrieved
grounding, long-document chunk/map-reduce, and per-turn token measurement. Run
the local retriever first and inspect its source lineage. Optional provider
work can replace the mock answer or add an embedding/retrieval backend, but
must keep metadata filters before generation, citations after it, environment
configuration, a token budget, and an offline mode. Do not commit policy
archives or model credentials.

ETL and scheduling experience is a useful way to explain memory, lineage, and
windowing; it does not restrict the range of actual LMS support and
retrieval demos.
