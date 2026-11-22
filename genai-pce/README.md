# Generative AI, Prompting and Context Engineering

LMS course: [Generative AI, Prompting and Context Engineering B-22](https://lms.snvaveranda.com/course/view.php?id=249)

The existing abbreviated module folders are retained to match the repository convention.

## Study workflow

The material assumes strong data-pipeline and operational experience but no
prior LLM expertise. SQL tables are analogous to structured records, ETL
pipelines to prompt/context workflows, job exit codes to validation and
fallback decisions, and schedulers to orchestration—while model output is
probabilistic rather than deterministic like a normal transformation.

Each module is organized as:

- `docs/README.md` — links to the protected LMS presentation, learning objectives, and slide-to-topic map
- `docs/NOTES.md` — expanded beginner implementation notes based on the presentation,
  with ETL/control-flow analogies, worked examples, failure analysis, and graded exercises
- `examples/` — medium-complexity, offline-capable exercises for hands-on practice

Recommended sequence:

1. Review the slide map in `docs/README.md`.
2. Read the relevant mental model and glossary in `docs/NOTES.md`.
3. Trace the deterministic example by hand, then run it before changing
   parameters.
4. Introduce one variation at a time and compare output quality, cost, latency,
   and reliability.
5. Treat every generated response as untrusted data until a validator checks
   its format and policy constraints.
6. Complete the extension challenges in `examples/README.md`.

Examples use mocks or local algorithms by default. Any real model provider integration should be supplied later behind the documented interface rather than hard-coded credentials.

## Module map

| Module | Focus |
| --- | --- |
| `M1_GenAI_LLM_Foundations` | Generative AI and LLM foundations |
| `M2_Transformer_Architectures` | Tokenization, attention, and transformer mechanics |
| `M3_Working_with_LLMs` | APIs, SDKs, parameters, and open-source models |
| `M4_Prompt_Engineering_Essentials` | Prompt structure, constraints, and evaluation |
| `M5_Advanced_Prompting_Techniques` | Advanced reasoning and prompting patterns |
| `M6_Context_Engineering` | Memory, windowing, retrieval, and chunking |
| `M7_Structured_Outputs_Tool_Use` | Structured outputs, function calling, and tools |
| `M8_Prompt_Optimization_Evaluation_DSPy` | Prompt evaluation, optimization, and DSPy concepts |
