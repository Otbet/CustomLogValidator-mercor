"""Custom Log Validator - Streamlit UI.

Checks whether a list of test methods appears in a blob of log output.
"""

from __future__ import annotations

import html

import streamlit as st

from validator import parse_test_names, summarize, validate

st.set_page_config(page_title="Custom Log Validator", page_icon="🪵", layout="wide")

STYLES = """
<style>
  .block-container { padding-top: 2rem; }
  .result-row {
    display: flex; align-items: center; justify-content: space-between;
    gap: 1rem; padding: 0.7rem 1rem; margin-bottom: 0.5rem;
    border-radius: 8px; border-left: 6px solid transparent;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  }
  .result-row.found { background: rgba(33, 195, 84, 0.12); border-left-color: #21c354; }
  .result-row.missing { background: rgba(255, 75, 75, 0.12); border-left-color: #ff4b4b; }
  .result-name { font-weight: 600; word-break: break-all; }
  .result-meta { font-size: 0.8rem; opacity: 0.75; white-space: nowrap; }
  .badge {
    padding: 0.2rem 0.65rem; border-radius: 999px; font-size: 0.75rem;
    font-weight: 700; letter-spacing: 0.03em; white-space: nowrap; color: #fff;
  }
  .badge.found { background: #1a9c45; }
  .badge.missing { background: #d93025; }
</style>
"""
st.markdown(STYLES, unsafe_allow_html=True)

header_left, header_right = st.columns([5, 1])
with header_left:
    st.title("Custom Log Validator")
    st.caption("Paste your logs and the test methods you expect to find in them.")
with header_right:
    st.write("")
    validate_clicked = st.button("Validate", type="primary", use_container_width=True)

logs_col, tests_col = st.columns([3, 2])
with logs_col:
    logs = st.text_area("Logs content", height=360, placeholder="Paste log output here...")
with tests_col:
    tests_raw = st.text_area(
        "Test methods",
        height=360,
        placeholder="One per line (commas and semicolons also work):\n\ntestLoginSuccess\ntestLogoutRedirect",
    )
    case_sensitive = st.checkbox("Case sensitive", value=False)
    whole_word = st.checkbox("Match whole method name only", value=False)

if validate_clicked:
    st.session_state["run"] = {
        "logs": logs,
        "tests_raw": tests_raw,
        "case_sensitive": case_sensitive,
        "whole_word": whole_word,
    }

run = st.session_state.get("run")

st.divider()

if not run:
    st.info("Enter logs and test methods, then click **Validate**.")
    st.stop()

test_names = parse_test_names(run["tests_raw"])

if not run["logs"].strip():
    st.warning("No logs provided - paste the log content you want to search.")
    st.stop()
if not test_names:
    st.warning("No test methods provided - add at least one method name.")
    st.stop()

results = validate(
    run["logs"],
    test_names,
    case_sensitive=run["case_sensitive"],
    whole_word=run["whole_word"],
)
stats = summarize(results)

st.subheader("Results")
total_col, found_col, missing_col = st.columns(3)
total_col.metric("Test methods", stats["total"])
found_col.metric("Found", stats["found"])
missing_col.metric("Not found", stats["not_found"])

only_missing = st.toggle("Show only missing", value=False)

rows = [r for r in results if not r.found] if only_missing else results
if not rows:
    st.success("Every test method was found in the logs.")

for result in rows:
    state = "found" if result.found else "missing"
    label = "FOUND" if result.found else "NOT FOUND"
    if result.found:
        preview = ", ".join(str(n) for n in result.line_numbers[:5])
        if len(result.line_numbers) > 5:
            preview += f", +{len(result.line_numbers) - 5} more"
        meta = f"{result.occurrences} hit(s) &middot; line(s) {preview}"
    else:
        meta = "no match in logs"
    st.markdown(
        f'<div class="result-row {state}">'
        f'<span class="result-name">{html.escape(result.name)}</span>'
        f'<span class="result-meta">{meta}</span>'
        f'<span class="badge {state}">{label}</span>'
        f"</div>",
        unsafe_allow_html=True,
    )

report = "\n".join(
    f"{'FOUND' if r.found else 'NOT FOUND'},{r.name},{r.occurrences}," + " ".join(map(str, r.line_numbers))
    for r in results
)
st.download_button(
    "Download report (CSV)",
    data="status,test_method,occurrences,line_numbers\n" + report + "\n",
    file_name="log_validation_report.csv",
    mime="text/csv",
)
