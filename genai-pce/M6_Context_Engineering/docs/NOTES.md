# Module 6 Notes: Context Engineering, Memory, and Retrieval

## 1. Context is selected state

Context is the task information included in a model call:

```text
trusted instructions
+ current user input
+ recent conversation
+ retrieved evidence
+ tool state/results
+ output reservation
```

It is not “all information we own.” The context window is a bounded staging area, so
selection, placement, freshness, permission, and lineage matter. In data terms, it is a
materialized input view; the view must have the correct joins and access filters.

## 2. Why context engineering follows prompts

A strong prompt with the wrong policy is still wrong. A context pipeline must:

1. identify the user's task and tenant;
2. enforce document authorization before relevance ranking;
3. retrieve relevant, current source chunks;
4. preserve source IDs and effective dates;
5. fit the evidence with task/history into the token budget;
6. detect missing evidence and abstain;
7. make every answer traceable.

Retrieval-augmented generation (RAG) reduces dependence on facts memorized during
training. It cannot rescue bad retrieval, stale sources, or weak access controls.

## 3. Chunking and metadata

Chunking splits documents into retrievable units. A chunk is like a small staged record:

```text
doc_id, tenant, jurisdiction, effective date, heading, offset, text, version
```

Strategies:

| Strategy | Strength | Risk |
| --- | --- | --- |
| Fixed token/character/word window | Simple and predictable | Splits a condition from its definition |
| Recursive separators | Keeps headings/paragraphs before smaller boundaries | Still may split needed relationships |
| Semantic grouping | Groups related meaning | Variable, costly, difficult to reproduce |
| Parent/child hierarchy | Retrieves small evidence and retains larger context | More storage and retrieval logic |

Overlap repeats nearby words across chunks so a boundary has a better chance of
preserving local continuity. It increases storage and token/retrieval cost. Use measured
recall instead of “large overlap is safest.”

## 4. Retrieval step-by-step

1. Validate query, tenant, jurisdiction, and requested limit.
2. Apply authorization filters to candidate records.
3. Generate lexical terms or an embedding as allowed by the implementation.
4. Rank eligible chunks for relevance and freshness.
5. Deduplicate repeated or parent/child content.
6. Select a bounded evidence set.
7. Include source metadata in the prompt.
8. Require citations/faithfulness checks in the answer.
9. Return “insufficient evidence” if no approved match exists.

**Critical:** embedding similarity or a high keyword count is not permission. Filter
authorization before ranking and verify it again at data access boundaries.

## 5. Context budget walkthrough

```text
window limit             16,000
system/task/policy        1,000
recent turns              1,500
retrieved policy          4,500
tool results                500
reserved answer           1,500
margin/overhead             500
                         ------
available/planned         9,500
```

Tokenizers differ. Reserve answer space and tool expansion; log actual usage and any
truncation. A 16K window does not mean 16K should be filled.

## 6. Conversation and memory types

| State | Lifetime | Use | Control |
| --- | --- | --- | --- |
| Recent-turn buffer | Current thread, last `n` turns | Immediate pronoun/topic continuity | Token bound and deletion |
| Summary | Replaces older transcript for session | Compress long interactions | Preserve source/facts; mark lossy |
| Checkpoint | Workflow run | Resume a multi-step job | Version state and idempotency |
| Structured store | Defined user/tenant lifecycle | Stable approved facts/preferences | Schema, provenance, expiry, correction |
| Vector/document index | Corpus lifecycle | Evidence retrieval | Access, freshness, re-indexing, deletion |

A durable customer preference is not the same as temporary assistant wording. Never
persist an unvalidated assertion as a fact. Separate tenants/users and implement data
subject deletion.

## 7. Worked retrieval case

Question:

```text
How quickly are EU refunds reviewed?
tenant=acme, jurisdiction=EU
```

Approved source:

```text
POL-EU-24, acme, EU, 2024:
"EU refunds are reviewed within ten business days..."
```

Unauthorized/nonmatching source:

```text
POL-EU-PRIVATE, other, EU, 2025
```

The output must cite only `POL-EU-24` and state ten business days. Asking for “private
refund” under tenant `acme` must not retrieve the `other` source. `context_engine.py`
filters metadata, ranks matching chunks, and preserves evidence IDs.

## 8. RAG quality components

Measure separate stages:

- **retrieval recall:** did required source chunks appear?
- **ranking:** where did they appear?
- **permission isolation:** did unauthorized chunks stay excluded?
- **faithfulness:** is the answer supported by retrieved sources?
- **answer correctness:** does the supported response solve the task?
- **freshness:** was the effective/superseding policy used?
- **format:** are citations and abstention machine-checkable?
- **operations:** token cost, retrieval latency, index freshness, answer latency.

An answer can be fluent and supported by a retrieved but superseded document. “Relevant”
and “current” are independent checks.

## 9. Cost, latency, and reliability

Retrieval avoids sending the whole corpus, but embeddings, indexes, chunk storage, and
ranking cost money/operations. More chunks consume input tokens and can raise time to
first token. Cross-encoder reranking may improve evidence selection but adds latency.
Caching can help repeat questions but must respect tenant and freshness boundaries.

Plan refresh and invalidation:

```text
source changed -> new version indexed -> old version superseded
-> cache invalidated -> tests prove expected citation changed
```

## 10. Failure analysis

| Symptom | Trace |
| --- | --- |
| Correct source exists, no answer evidence | Chunk split, lexical/embedding retrieval, filter, limit, or query rewrite |
| Answer cites private other-tenant source | Authorization filter violated; treat as a security incident |
| Old policy used | Effective-date/supersession metadata or cache/index failure |
| Two chunks say opposite things | Version/conflict resolution missing |
| Answer fluent but unsupported | Faithfulness and citation gate missing |
| Long chat loses early detail | Windowing/summary loss; preserve structured fact/source |
| Cost rises sharply | Too much overlap, high `k`, full history, repeated tool content |

## 11. Debugging checklist

1. Inspect normalized query, tenant, role, jurisdiction, and effective-time filters.
2. Confirm eligible corpus count before ranking.
3. Inspect source IDs, scores, versions, headings, and offsets for top `k`.
4. Confirm required and conflicting chunks are represented in tests.
5. Calculate final token budget and detect truncation.
6. Compare answer claims one-by-one to cited chunks.
7. Delete/expire a source in a test and verify cache/index behavior.
8. Run cross-tenant and unrelated-document negative tests.

## 12. Common misconceptions

- **“Vector search is access control.”** It ranks; application filters authorize.
- **“A larger context removes retrieval.”** It costs more and still has stale/irrelevant
  data risks.
- **“A summary is the original.”** Compression loses detail and should remain traceable.
- **“Highest similarity is the best source.”** Freshness, authority, and coverage also matter.
- **“Memory can store anything.”** Use schema, consent, retention, and deletion.
- **“RAG prevents hallucination.”** It provides evidence; answer faithfulness still must be checked.

## 13. Graded exercises

1. **Metadata (15):** Design a chunk lineage schema for tenant, policy version, effective
   date, source offset, and confidentiality.
2. **Budget (15):** Allocate a 16K window among instructions, history, evidence, tools,
   output, and margin.
3. **Retrieval (20):** Explain retrieval filters and ranking in `context_engine.py`, then
   predict its two source queries before running it.
4. **Failure lab (25):** Create conflicting and outdated policy cases; require abstention
   or conflict escalation.
5. **Operations (25):** Specify ingestion, re-indexing, cache invalidation, deletion,
   metrics, SLOs, and rollback for a RAG corpus.
