# Module 8: AI Pair Programming Fundamentals

- **LMS course:** [Modern Python & AI-Assisted Development](https://lms.snvaveranda.com/course/view.php?id=248)
- **Presentation URL/ID:** `https://lms.snvaveranda.com/mod/resource/view.php?id=15495` / `15495`

## Deck map

| Slides | Topic |
| --- | --- |
| 1–8 | Vibe coding fundamentals, workflow, and outcomes |
| 9–12 | AI-assisted development tool landscape |
| 13–19 | Copilot architecture, capabilities, and setup |
| 20–25 | Copilot Chat and iterative context-aware work |
| 26–32 | Quality risks, validation, prompt controls, and AI-assisted testing |
| 33–46 | Prompt/context engineering and reusable refinement patterns |
| 47–50 | Summary and review |

## Learning objectives

Frame implementation intent, provide useful project context, work iteratively with Copilot, configure the development environment, detect generated-code risks, create and execute tests, and validate security, correctness, and maintainability.

> These notes summarize the protected deck for study; they do not reproduce its slide text, examples, or artwork.

## LMS demonstration walkthrough

- **Resources:** <https://lms.snvaveranda.com/mod/resource/view.php?id=15496>, <https://lms.snvaveranda.com/mod/resource/view.php?id=15497>, <https://lms.snvaveranda.com/mod/resource/view.php?id=15498>, and <https://lms.snvaveranda.com/mod/resource/view.php?id=15499>.
- **Actual assignment:** set up/authenticate Copilot in VS Code; generate an average function and refactor a customer formatter; generate and diagnose pytest tests for a price validator; then improve an order-pricing function with structured, focused, example-driven, and follow-up prompts.
- **Input/data shape:** short Python list inputs, customer name/email/city strings, a numeric price, and order item records with `price`/`quantity` plus a discount. No LMS dataset is required.
- **Beginner workflow:** verify Copilot availability, create a tiny file, state expected behavior before prompting, review the complete suggestion, accept only understood changes, run focused code/tests, use a failing assertion as evidence, and finish by checking the diff.
- **Relationship to current examples:** `ai_change_gate.py` is an **original extension beyond the four LMS demonstrations**. It deterministically summarizes evidence and risks; it does not call Copilot or prove approval.
- **Deliberate practice:** compare a vague and structured prompt, predict edge cases before generation, introduce one incorrect expectation, ask for an explanation rather than a rewrite, and require pytest plus a human requirement review.

See the detailed walkthrough at the end of `NOTES.md`.
