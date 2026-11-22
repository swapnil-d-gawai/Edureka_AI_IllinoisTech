# Module 3: Working with LLMs

- **LMS presentation:** https://lms.snvaveranda.com/mod/resource/view.php?id=8630
- **Presentation ID:** `8630`
- **Course:** [Generative AI, Prompting and Context Engineering](https://lms.snvaveranda.com/course/view.php?id=249)

## Deck map

1. Provider and model landscape, including hosted and open-weight options
2. Summarization, question answering, translation, and code-generation use cases
3. Temperature, top-p, output limits, stop sequences, and decoding strategies
4. Tool calls, deployment, retries, logging, token efficiency, cost, and latency

## Learning objectives

- Compare API and local-deployment operating models.
- Configure generation controls for a task's reliability and diversity needs.
- Explain greedy, beam, and sampling behavior.
- Design safe tool-calling and retry boundaries.
- Estimate token cost and capture latency, quality, and failure telemetry.

> These notes summarize and interpret the presentation for study and practice; they do not reproduce the deck.

## LMS demonstration walkthrough

- **Demonstration resource:** https://lms.snvaveranda.com/mod/resource/view.php?id=8631
- **Actual LMS work:** a developer lab configures Gemini, lists supported
  models, makes basic/chat API calls, examines responses and errors, compares
  temperature/top-p/top-k/token-limit/stop controls, and measures prompt,
  context, and batch token efficiency.
- **Inputs and expected results:** inputs are prompts for explanation, code,
  translation, a multi-turn Python conversation, creative generation, and
  verbose-versus-concise requests. Expected evidence includes response text,
  candidate/finish/safety metadata, character or word measures, estimated
  input/output totals, batch savings, and controlled behavior after context
  trimming. Exact language varies.
- **Beginner workflow:** configure the key only through the environment;
  discover models and limits; make one request; inspect status/finish reason;
  add a timeout and retry boundary; hold prompt/model constant while changing
  one generation control; then estimate tokens before and after shortening,
  batching, or windowing. Log observations without logging secrets.
- **Safe/offline counterpart:** `examples/llm_gateway.py` is the default route:
  its mock simulates throttling and malformed output and demonstrates the
  application's validation/retry contract without a network call.
- **Relationship to the original example:** the gateway wraps the same
  request/response lifecycle as the LMS Gemini calls, but its deterministic
  provider makes failures reproducible for a beginner operations workflow.
- **Deliberate practice:** define acceptance checks for a 50- and 150-token
  limit, predict whether a low top-p response will be more or less diverse,
  and run the experiment with retry/latency/token telemetry captured for
  comparison. API execution is optional.
