# Module 6: AI APIs and FastAPI Backends

- **LMS course:** [Modern Python & AI-Assisted Development](https://lms.snvaveranda.com/course/view.php?id=248)
- **Presentation URL/ID:** `https://lms.snvaveranda.com/mod/resource/view.php?id=8621` / `8621`

## Deck map

| Slides | Topic |
| --- | --- |
| 1–10 | REST, HTTP methods, lifecycle, and status codes |
| 11–18 | FastAPI structure, routers, dependencies, Pydantic request/response models |
| 19–22 | Async AI endpoints |
| 23–27 | Server-Sent Events and streaming |
| 28–31 | Uploads and document-processing pipeline |
| 32–36 | Uvicorn, Swagger, and API testing |
| 37–40 | Summary and review |

## Learning objectives

Design resource-oriented HTTP APIs; validate contracts with Pydantic; structure services with dependency injection; use async I/O; stream SSE safely; validate uploads; and verify API behavior through tests and generated documentation.

> These notes summarize the protected deck for study; they do not reproduce its slide text, examples, or artwork.

## LMS demonstration walkthrough

- **Resource:** <https://lms.snvaveranda.com/mod/resource/view.php?id=8622>.
- **Actual assignment:** build a FastAPI service with a Pydantic prompt request, a Groq-backed `POST /generate`, a structured JSON response, environment-based configuration, Uvicorn/Swagger testing, and a programmatic client.
- **Input/data shape:** request is a text `prompt`; a representative response contract has `response`, `model`, and `status` strings. A local `.env` supplies a real key/model and must remain outside version control.
- **Beginner workflow:** (1) define models, (2) add a health route, (3) test a deterministic local stub, (4) run Uvicorn and inspect `/docs`, (5) submit valid and invalid JSON, (6) add the provider behind a replaceable dependency, (7) verify status/body together.
- **Relationship to current examples:** `support_triage_api.py` is an **original extension beyond the LMS demonstration**. It keeps the FastAPI/Pydantic/provider-boundary lesson but exposes ticket-oriented contracts and a local deterministic classifier rather than calling Groq by default.
- **Deliberate practice:** use a synthetic prompt, omit the prompt, add an unknown field, simulate provider failure, and write an expected status/schema table before testing. Never put a key in docs, tests, logs, or Git.

See the detailed walkthrough at the end of `NOTES.md`.
