# Module 1 Notes: Generative AI and LLM Foundations

## 1. Where to start

No machine-learning background is required. If you have built SQL queries, Informatica
mappings, Unix jobs, or AutoSys/TWS schedules, keep those ideas: a GenAI application is
still a pipeline with inputs, transformations, controls, observability, and failure
paths. The difference is that one transformation produces a **probabilistic result**
rather than a deterministic row or file.

Think of a model call as a specialized service:

```text
validated input + instructions + selected evidence
                    |
                    v
        probabilistic language model
                    |
                    v
   candidate output --> validate --> approve/refuse/use
```

The final application action must not be “whatever the model wrote.”

## 2. Essential vocabulary

| Term | Plain-language meaning | Familiar analogy |
| --- | --- | --- |
| Generative AI | Produces new content from learned patterns | A transformation that synthesizes a new record rather than only joining existing ones |
| Model | A trained mathematical function with many adjustable **parameters** | Executable program plus learned configuration, but not ordinary source code |
| LLM | A model trained extensively on language and used to generate or understand text | A text service with broad learned behavior |
| Token | A piece of text such as a word, part of a word, space, or punctuation | A small parsing unit, not necessarily an SQL “word” or whitespace field |
| Prompt | The task input: instructions, context, evidence, examples, and question | A job's command line plus runtime parameters plus source data |
| Context window | Maximum token state the model can consider for one call, including the intended output budget | A bounded staging area shared by all inputs and output |
| Hallucination | Fluent unsupported or false content | A row with a plausible-looking value but no source lineage |
| Classification | Choosing one label from a known set | A deterministic or statistical router |

**Do not confuse model parameters with prompt parameters.** Model parameters are learned
numbers fixed in the deployed model. Prompt parameters are runtime controls such as
temperature or output length.

## 3. Generative versus discriminative systems

A **discriminative model** answers “which category?” from a finite set:

```text
Input: "The duplicate invoice was charged twice"
Output: billing
```

A **generative model** can synthesize:

```text
Input: a billing ticket + an approved refund policy
Output: a draft acknowledgement tailored to the customer
```

Use the smallest reliable mechanism. A mapping, SQL rule, parser, or classifier can be
better than an LLM when the allowed outcomes are narrow and stable. Use an LLM for
language variation, synthesis, summarization, explanation, and ambiguous text. A robust
production design often combines both.

## 4. Tokens, embeddings, and next-token generation

### Step-by-step

1. **Tokenize:** split text into model-specific token IDs. `refund` may be one token or
   several depending on tokenizer and model.
2. **Embed:** turn each token ID into a numeric vector. Similar vector patterns can help
   the model represent semantic relationships; this is not a readable database of facts.
3. **Mix context:** the transformer uses attention to let token representations relate to
   other tokens.
4. **Predict:** compute a score for every possible next token.
5. **Choose:** greedy, sampling, or another decoding method picks one token.
6. **Repeat:** append that token and predict again until completion, stop, or token limit.

The model does not “retrieve the true sentence.” It predicts a likely sequence from
learned patterns and the current context. Like a lookup without a source key, fluency
does not prove provenance.

### Token walkthrough

Assume a tokenizer produces:

```text
"Refund ID 12345" -> ["Refund", " ID", " 123", "45"]
```

This is illustrative; real tokenizers differ. Four characters do not necessarily mean
one token, and a long numeric identifier can consume several tokens. Exact counts must
come from the selected model's tokenizer or provider usage metadata.

### Context walkthrough

If a window is 32,000 tokens and you reserve 2,000 for output, at most 30,000 remain for
the system instructions, user input, history, evidence, and tool output. Overflow may
truncate data. Treat this as a job that writes to a fixed partition: check the allocation
before execution instead of discovering missing policy late.

## 5. Model families

| Family | Typical shape | Good fit |
| --- | --- | --- |
| Encoder-only (BERT-like) | Reads input in both directions | Classification, search relevance, extraction |
| Decoder-only (GPT-like) | Generates left to right | Chat, drafting, synthesis, general assistants |
| Encoder-decoder (T5-like) | Reads a source then generates a target | Translation, source-to-summary transformations |

These are starting points, not guarantees. Benchmark the task.

## 6. LLM lifecycle as an ETL/control workflow

```text
requirements
   -> data governance -> training/adaptation -> offline evaluation
   -> approval -> deployment -> monitoring -> incident/rollback
```

1. **Requirements:** allowed tasks, prohibited actions, service target, privacy rules.
2. **Data preparation:** source, filter, de-identify, label, partition, and record lineage.
3. **Pretraining:** broad language pattern learning performed by a model provider.
4. **Fine-tuning/instruction tuning:** further task or behavior adaptation.
5. **Evaluation:** held-out examples, safety tests, cost, and latency.
6. **Alignment:** techniques intended to make behavior follow user and safety preferences.
7. **Deployment:** version, access controls, rate limits, timeouts, rollback.
8. **Monitoring:** quality samples, validity, safety, drift, usage, and incidents.

Training is closer to producing a reusable executable artifact than to composing one
mapping. A prompt change is faster but is still a release and should be versioned.

## 7. Worked industry scenario

A retailer receives 50,000 customer messages per day. A bad design lets an LLM both
interpret every ticket and perform a refund. A controlled design is:

```text
ticket -> validate -> cheap classifier/router -> policy retrieval
       -> draft-only model -> schema check -> policy gate
       -> approved reply OR human queue
```

**Example input**

```text
Ticket A-102: "Please refund the duplicate charge on my order."
```

**Intermediate decisions**

```text
category = refund
draft = "We can review the return..."
policy result = human_approval_required
approved = false
```

**Output**

```text
A-102: category=refund
approved=false
action=human_approval_required
draft remains a draft; no money moves
```

This is the pattern in `examples/support_intake.py`: the mock provider generates text,
while application code owns validation and policy.

## 8. Model size, cost, latency, and reliability

- More parameters can add capability and serving cost, but do not guarantee better task
  accuracy. Evaluate small models first.
- Input and output tokens drive metered cost. Long histories and verbose reasoning can be
  expensive even when answer quality is unchanged.
- Latency includes queueing, time to first token, generation time, retries, and downstream
  validation. Tail latency (p95/p99), not only average, affects batch and online jobs.
- A fluent response is not a successful transaction. Reliability includes valid format,
  correct evidence, authorization, and safe fallback.
- Fewer model calls are usually cheaper and easier to recover, but decomposition can
  improve hard tasks. Measure the complete workflow.

As with AutoSys/TWS, define timeouts, retries, dependencies, terminal states, rerun
behavior, and ownership. LLM calls must be idempotent or separated from side effects.

## 9. Failure analysis

| Symptom | Likely causes | Safe diagnostic |
| --- | --- | --- |
| Empty or truncated answer | Output cap, timeout, context overflow | Log usage/stop reason; reproduce with fixed request |
| Plausible but false policy | Missing/old evidence, hallucination | Trace source IDs and approved effective date |
| Different output on rerun | Sampling, provider/model variation | Record seed/settings/model version; repeat |
| Customer data in logs | Whole-prompt logging | Inspect redaction and retention controls |
| Bad business action | Model output trusted directly | Add schema, policy, authorization, and approval gate |
| High cost | Long context, many retries, oversized model | Compare tokens/calls/model by use case |

## 10. Debugging checklist

1. Freeze and record the exact input, model version, prompt version, settings, and provider.
2. Classify the failure: transport, timeout, rate limit, invalid request, model quality,
   schema, retrieval, policy, or application bug.
3. Inspect token usage and stop reason before changing prompt wording.
4. Compare expected fields and sources, not just prose appearance.
5. Reproduce with the offline mock or fixed fixture.
6. Change one variable at a time.
7. Verify safe fallback and rollback on a failing case.

## 11. Common misconceptions

- **“An LLM understands the world like a person.”** It produces learned statistical
  continuations; apparent understanding must be tested for the task.
- **“Lower temperature makes an answer true.”** It reduces randomness; it does not add facts.
- **“A larger model is always better.”** It may be slower and costlier with no task gain.
- **“Tokens are words.”** They can be pieces of words, spaces, or multiple-character groups.
- **“A prompt is just wording.”** It is a versioned production input with a security and
  privacy boundary.
- **“A confident sentence is evidence.”** Require lineage, validation, or human approval.

## 12. Graded exercises

1. **Foundation (10):** Rewrite the tokenization definition for a SQL colleague and give
   one non-word token example.
2. **Application (20):** Draw an intake control-flow diagram with a retry boundary and a
   human-approval node.
3. **Analysis (25):** Run `support_intake.py`; explain why each of its four outcomes is or
   is not safe to send or execute.
4. **Debugging (20):** Modify only a local copy of one ticket to force a different
   category. Predict the result before running it and explain the data-lineage impact.
5. **Design (25):** Propose a small-model/LLM hybrid, including p95 latency, token-cost,
   privacy, abstention, and rollback criteria. State when you would reject the LLM.

## 13. Exit check

Before Module 2, explain without ML vocabulary: (1) how text is split into pieces,
(2) how the model proposes another piece, (3) why a proposal is not proof, and
(4) where deterministic controls belong in the pipeline.
