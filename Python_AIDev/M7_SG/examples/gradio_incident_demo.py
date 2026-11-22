"""Minimal Gradio front end for the same local triage function."""

from __future__ import annotations

import gradio as gr

from incident_triage import analyze_incident


def triage(subject: str, details: str) -> str:
    """Adapt shared rule results and validation failures to Gradio components."""
    try:
        result = analyze_incident(subject, details)
    except ValueError as exc:
        raise gr.Error(str(exc)) from exc
    return (
        f"## Triage result\n\n- **Severity:** {result['severity']}\n"
        f"- **Team:** {result['team']}\n- **Rationale:** {result['rationale']}"
    )


demo = gr.Interface(
    fn=triage,
    inputs=[gr.Textbox(label="Subject"), gr.Textbox(label="Details", lines=5)],
    outputs=gr.Markdown(),
    title="Incident triage demo",
    description="Local deterministic rules only; no external calls.",
    examples=[
        ["Checkout unavailable", "All users receive an error during payment"],
        ["API requests are slow", "A subset of requests has intermittent latency"],
    ],
)

if __name__ == "__main__":
    demo.launch(show_error=True)
