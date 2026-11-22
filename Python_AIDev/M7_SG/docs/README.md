# Module 7: AI-Native Apps with Streamlit and Gradio

- **LMS course:** [Modern Python & AI-Assisted Development](https://lms.snvaveranda.com/course/view.php?id=248)
- **Presentation URL/ID:** `https://lms.snvaveranda.com/mod/resource/view.php?id=8623` / `8623`

## Deck map

| Slides | Topic |
| --- | --- |
| 1–12 | Streamlit layouts, widgets, state, caching, and streaming chat |
| 13–19 | Gradio inputs, outputs, components, and layouts |
| 20–24 | Sharing, Hugging Face Spaces, and dependencies |
| 25–28 | Connecting UI applications to FastAPI |
| 29–32 | Streamlit versus Gradio selection |
| 33–36 | Summary and review |

## Learning objectives

Build stateful Streamlit interactions, cache expensive work correctly, stream chat output, compose Gradio demos, connect front ends to validated APIs, and choose an interface strategy and deployment shape appropriate to the audience.

> These notes summarize the protected deck for study; they do not reproduce its slide text, examples, or artwork.

## LMS demonstration walkthrough

- **Resources:** <https://lms.snvaveranda.com/mod/resource/view.php?id=8624> and <https://lms.snvaveranda.com/mod/resource/view.php?id=8625>.
- **Actual assignment:** 8624 builds a Streamlit chat UI over a FastAPI Server-Sent Events endpoint that streams Groq responses and stores complete conversation history. 8625 builds a Gradio assistant over FastAPI, with prompt, optional file/image controls, structured JSON response, and shareable launch workflow.
- **Input/data shape:** Streamlit request history is a list of `{role, content}` messages. Gradio's POST body adds a text prompt and optional image encoding/MIME fields; displayed responses carry generated text, model, and status. Treat upload bytes and all UI text as untrusted.
- **Beginner workflow:** start the backend, prove health outside the UI, build one form/control, preserve a short synthetic history, display complete chunks in order, store only the final assistant message, then simulate timeout/backend failure and a non-streaming fallback.
- **Relationship to current examples:** `streamlit_incident_app.py` and `gradio_incident_demo.py` are **original offline extensions beyond the LMS live-provider demonstrations**. They use the same UI responsibilities but share deterministic incident triage and do not require Groq.
- **Deliberate practice:** submit the same three-message history in Streamlit and through the backend directly; interrupt one stream; test empty/oversized input; verify both UIs produce the same model-independent result when using the local example.

See the detailed walkthrough at the end of `NOTES.md`.
