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
