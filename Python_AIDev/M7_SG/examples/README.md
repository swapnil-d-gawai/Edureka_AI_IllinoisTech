# Incident triage workbench

This directory demonstrates the same deterministic triage logic through Streamlit and Gradio. Inputs are validated, Streamlit stores an explicit session history, the result is cached by content, and Gradio renders a Markdown contract. No provider or backend is contacted.

## Run

```bash
streamlit run streamlit_incident_app.py
python gradio_incident_demo.py
```

Install only if absent: `pip install streamlit gradio`. Streamlit should show a form, local result, and history. Gradio should show two examples and produce the same severity/team result. API/provider extensions should first add timeouts and response validation.

Both UIs import `incident_triage.py`, which remains independent of either frontend framework.

Challenges: introduce an environment-controlled FastAPI base URL, add a file input and bounded text extraction, stream the result, add backend-timeout UX, and make the two UIs share a real service module.

## LMS bridge

LMS resources 8624 and 8625 respectively add a Streamlit-to-SSE/FastAPI streaming flow and a Gradio-to-FastAPI flow with optional file/image controls. First model the `{role, content}` history and three fixed stream chunks locally, then compare that shape with `docs/NOTES.md`. These incident UIs are original, offline extensions and intentionally keep live Groq, share links, uploads, and keys out of the default path.
