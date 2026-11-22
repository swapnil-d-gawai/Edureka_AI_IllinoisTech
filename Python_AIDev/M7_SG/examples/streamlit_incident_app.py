"""Local-first Streamlit incident triage workbench."""

from __future__ import annotations

import streamlit as st

from incident_triage import analyze_incident

# Cache only the deterministic value function; the UI-specific session history remains explicit.
analyze_incident = st.cache_data(analyze_incident)


st.set_page_config(page_title="Incident triage", page_icon="🛠️", layout="wide")
st.title("Incident triage workbench")
st.caption("Deterministic local mode. No prompt or incident data leaves the browser server.")

if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.header("Mode")
    st.selectbox("Classifier", ["Local rules (active)", "FastAPI backend (extension)"], disabled=True)
    st.slider("Confidence threshold", 0, 100, 70, disabled=True)
    st.info("Provider and backend integrations are intentionally disabled in this learning example.")

col1, col2 = st.columns([3, 2])
with col1:
    with st.form("incident"):
        subject = st.text_input("Subject", max_chars=120, placeholder="Checkout is unavailable")
        details = st.text_area("Details", height=160, max_chars=5_000)
        submitted = st.form_submit_button("Analyze", type="primary")

    if submitted:
        if len(subject.strip()) < 3 or len(details.strip()) < 10:
            st.error("Provide a subject (3+ characters) and details (10+ characters).")
        else:
            result = analyze_incident(subject.strip(), details.strip())
            st.session_state.history.append(
                {"subject": subject.strip(), **result}
            )
            st.success("Analysis complete")
            st.json(result)

with col2:
    st.subheader("Analyst history")
    if st.button("Clear history") and st.session_state.history:
        st.session_state.history = []
        st.rerun()
    if st.session_state.history:
        st.dataframe(st.session_state.history, hide_index=True, use_container_width=True)
    else:
        st.info("Submit an incident to create a local session record.")

st.divider()
with st.expander("Practice prompts"):
    st.markdown(
        "- `Database checkout is slow for some regions`\n"
        "- `All users cannot sign in after the release`\n"
        "- `Possible credential exposure in an uploaded log`"
    )
