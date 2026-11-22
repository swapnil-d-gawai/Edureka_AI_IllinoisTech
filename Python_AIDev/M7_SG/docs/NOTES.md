# Module 7 Notes: AI-Native Apps with Streamlit and Gradio

These notes align with the LMS topics for Streamlit layout/state/cache/chat, Gradio components/layouts, sharing/deployment, FastAPI integration, and choosing a front end. A UI is the visible edge of a workflow; business rules and durable services should remain testable without a browser.

## 1. UI and backend responsibilities

UI responsibilities:

- capture input,
- show progress and errors,
- keep interaction state,
- present or filter results,
- connect to a backend.

Backend responsibilities:

- authorize and validate,
- own durable data,
- apply business/model rules,
- call protected providers,
- enforce timeouts and rate limits.

Think of the UI as an operational console and FastAPI as the scheduler/service interface. A console may provide a manual preview, but it should not become the only copy of a production transformation.

## 2. Streamlit execution model

A Streamlit script reruns from top to bottom when a widget changes. This is the key mental model.

```python
name = st.text_input("Name")
if st.button("Run"):
    st.write(name)
```

After every interaction, ordinary local variables are reconstructed. Values that must survive reruns need `st.session_state`.

### Session state

Initialize before reading:

```python
if "history" not in st.session_state:
    st.session_state.history = []
```

Then append explicit records:

```python
st.session_state.history.append(result)
```

Do not assume state is durable or secret. It is cross-rerun browser/session state, not a database or browser-inaccessible credential vault.

## 3. Forms and layout

Wrap related inputs in a form so submission occurs once:

```python
with st.form("incident"):
    subject = st.text_input("Subject")
    submitted = st.form_submit_button("Analyze")
```

Without a form, each widget interaction can trigger reruns. The demo uses columns, sidebar configuration, an expander, status messages, JSON output, and a dataframe.

Layout:

- `st.sidebar` for secondary controls,
- `st.columns` for visual groups,
- `st.container`/`with` blocks for composition,
- `st.expander` for optional help.

Always keep essential outcomes and errors visible.

## 4. Caching: values versus resources

`st.cache_data` is for data/results that can be serialized, typically pure transformations:

```python
@st.cache_data
def parse(text):
    ...
```

`st.cache_resource` is for long-lived services/connections.

Every input affecting the result must contribute to the cache key. A function that reads a hidden global prompt, provider mode, or current file contents can return a stale result unless the key explicitly captures it.

The example wraps the deterministic:

```python
analyze_incident = st.cache_data(analyze_incident)
```

The strings are key inputs, so equal inputs can reuse equal results. Do not cache confidential or unbounded model output without retention policy.

## 5. Building and streaming chat

A chat interaction app usually:

1. initializes history,
2. renders prior user/assistant turns,
3. accepts a new prompt,
4. appends the user turn,
5. streams generated pieces,
6. accumulates once,
7. appends the complete assistant turn.

Never append each stream fragment as a separate history item. Keep a placeholder for progressive text, then store the complete result.

If generation fails halfway, show a clear degraded/failure state and decide whether partial text remains visible or is marked incomplete.

## 6. Gradio components

Gradio connects a Python function to inputs and outputs:

```python
demo = gr.Interface(
    fn=triage,
    inputs=[gr.Textbox(label="Subject"), gr.Textbox(label="Details")],
    outputs=gr.Markdown(),
)
```

The function shape must match the components:

- two input components → two function parameters,
- one output → one returned value (or the declared output shape),
- multiple outputs → a predictable tuple/list contract.

`gr.Error` turns a handled `ValueError` into a visible UI error. Do not expose an arbitrary traceback to public users.

## 7. Shared business logic

Both front ends import `analyze_incident` from `incident_triage.py`. This separation means:

- the rule can be tested without Streamlit/Gradio,
- both UIs produce equivalent fields,
- future backend/provider logic has one boundary.

`incident_triage.py` defines a frozen dataclass:

```python
Triage(severity, team, rationale)
```

The dataclass is a convenient internal record. The function returns a dictionary because JSON/UI boundaries usually prefer serializable public values.

## 8. Worked triage case

Input:

- subject: `Checkout unavailable`
- details: `All users receive an error during payment`

The function normalizes combined text to lowercase, recognizes `"unavailable"` and `"all users"`, and returns:

```json
{
  "severity": "high",
  "team": "service operations",
  "rationale": "Broad service impact detected"
}
```

Streamlit displays JSON/history. Gradio converts the same dictionary to Markdown. Their presentation differs; the rule result should not.

## 9. Validation and untrusted UI content

Treat fields and uploaded files as untrusted:

- enforce lengths,
- restrict accepted file types and bytes,
- validate backend responses before rendering,
- do not execute uploaded code,
- protect paths and filenames,
- consider HTML/Markdown injection,
- never include secrets in state or browser configuration.

A minimum-length check provides useful UX but is not a complete security boundary. Repeat authoritative validation in the backend.

## 10. Connect to FastAPI

Configuration:

```text
TRIAGE_API_BASE_URL=https://...
```

Client behavior:

1. construct a bounded request,
2. set finite connect/read timeout,
3. validate status and JSON schema,
4. map network/timeout/validation failures to UI-safe states,
5. show “backend unavailable” rather than fake a model answer.

Keep credentials on the server side. A public Gradio/Streamlit browser client should not receive provider API keys.

## 11. Deployment

Declare dependencies in a small manifest with compatible/pinned versions. Unnecessary model packages slow installation and add vulnerabilities.

Streamlit and Gradio may support temporary public sharing. That does not replace:

- authentication,
- access policy,
- confidential-data review,
- TLS/hosting,
- persistent storage,
- observability,
- backup and incident ownership.

Never put confidential incident data into a public demo.

## 12. Choosing Streamlit or Gradio

| Preference | Typical fit |
| --- | --- |
| app-like analytics workbench | Streamlit |
| quick function/model demonstration | Gradio |
| explicit rerun/session layout | Streamlit |
| a typed component interface with examples | Gradio |
| public model playground | Gradio |
| analyst dashboard with state/forms | Streamlit |

Both can call a FastAPI backend and both need production controls; the framework does not decide the system architecture.

## 13. Debugging checklist

1. Reproduce as a direct Python call to `analyze_incident`.
2. For disappearing state, inspect initialization and every rerun assignment.
3. For stale output, inspect all cache-key inputs.
4. Log UI-safe correlation/error categories, not full incident text.
5. For a blank Gradio result, confirm function return type/arity matches components.
6. For backend failure, test health and one request outside the UI.
7. Check version compatibility of Streamlit/Gradio with Python.
8. Clear only relevant session/cache state and rerun minimal input.

## 14. Common mistakes

- Expecting normal variables to survive a Streamlit rerun.
- Assuming widget state and durable database state are equivalent.
- Caching a hidden provider/global prompt dependency.
- Blocking the interface with no timeout.
- Returning HTML/Markdown unsafely from untrusted data.
- Putting provider credentials in the browser app.
- Enabling public sharing for confidential data.
- Duplicating business rules separately in each UI.

## 15. Practice

1. Add a session-state counter for successful submissions.
2. Add a region filter to history.
3. Add a deterministic Gradio example and one invalid input.
4. Cache the result and demonstrate the key changing after whitespace normalization.
5. Add an environment-controlled FastAPI base URL with a five-second timeout.
6. Show a disabled/degraded state when backend health fails.
7. Add a file input, but enforce type and 1 MB byte limits before content extraction.
8. Test that both UIs show exactly the same result for the same valid input.
