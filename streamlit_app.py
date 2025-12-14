import os
import json
import streamlit as st
from coordinator import Coordinator

st.set_page_config(
    page_title="AI Code Debugger",
    page_icon="🧠",
    layout="wide",
)

st.title("🔬 The Debugging Experiment")

st.markdown(
    "Paste your **buggy Python code** below. The system will:\n"
    "1. Analyze the bug\n"
    "2. Propose a fix\n"
    "3. Execute the fixed code\n"
    "4. Validate the result\n"
)

# Check API key
if "GEMINI_API_KEY" not in os.environ:
    st.error("GEMINI_API_KEY not found in environment. Check your .env or environment variables.")
    st.stop()

# Sidebar examples
with st.sidebar:
    st.header("Examples")
    example_choice = st.selectbox(
        "Choose example:",
        ["Custom", "Syntax Error", "Logic Error", "Runtime Error"],
    )

    examples = {
        "Syntax Error": """def greet(name)
    print("Hello", name)

greet("Santhosh")""",
        "Logic Error": """def double(x):
    return x + x + 1  # incorrect

print(double(5))  # should be 10""",
        "Runtime Error": """def safe_divide(a, b):
    return a / b

nums = [10, 5, 0]
for n in nums:
    print(safe_divide(10, n))""",
    }

# Main input area
st.subheader("💻 Buggy Python Code")

if example_choice != "Custom":
    default_code = examples[example_choice]
else:
    default_code = """# Paste your buggy Python code here
def your_function():
    pass
"""

code_input = st.text_area(
    "Code:",
    value=default_code,
    height=240,
)

col1, col2 = st.columns([1, 1])
with col1:
    run_btn = st.button("🚀 Debug Code", type="primary", use_container_width=True)
with col2:
    if st.button("🔄 Reset", use_container_width=True):
        st.rerun()

if run_btn:
    if not code_input.strip():
        st.warning("Please paste some Python code first.")
    else:
        coordinator = Coordinator(max_retries=2)

        with st.status("Running multi-agent debugging...", expanded=False) as status:
            result = coordinator.debug_code(code_input)

            if result["success"]:
                status.update(
                    label="✅ Debugging Complete - Code Fixed!",
                    state="complete",
                )
            else:
                status.update(
                    label="❌ Debugging Failed",
                    state="error",
                )

        # Summary section
        st.subheader("📊 Summary")

        if result["success"]:
            st.success(f"Code fixed successfully in **{result['attempts']}** attempt(s).")
        else:
            st.error(
                f"Could not fully fix the code after **{result['attempts']}** attempt(s). "
                "You may need to review the last suggested fix manually."
            )

        # Vertical: Original then Fixed
        st.subheader("🐛 Original Code (Buggy)")
        st.code(code_input, language="python")

        st.subheader("✨ Fixed Code")
        st.code(result.get("fixed_code", "# No fixed code generated"), language="python")

        # Bug analysis
        with st.expander("🔍 Bug Analysis", expanded=False):
            st.markdown(result.get("analysis", "No analysis available."))

        # Validation report (human-readable)
        with st.expander("🧪 Validation Report", expanded=False):
            raw_validation = result.get("validation", "")
            try:
                cleaned = (
                    raw_validation.replace("```json", "")
                    .replace("```", "")
                    .strip()
                )
                data = json.loads(cleaned)
                status_txt = data.get("validation", "UNKNOWN")
                reason = data.get("reason", "")
                remaining = data.get("remaining_issues", [])
                confidence = data.get("confidence", "Unknown")

                st.write(f"**Validation:** {status_txt}  _(confidence: {confidence})_")
                if reason:
                    st.write(f"**Reason:** {reason}")
                if remaining:
                    st.write("**Remaining Issues:**")
                    for issue in remaining:
                        st.write(f"- {issue}")
                else:
                    st.write("No remaining issues reported.")

            except Exception:
                if raw_validation:
                    st.write("Raw validation response:")
                    st.code(raw_validation)
                else:
                    st.info("No validation details available.")

        # Execution output
        exec_result = result.get("execution_result", {})
        with st.expander("⚙️ Execution Output", expanded=False):
            if exec_result.get("success"):
                st.write("**Status:** Success")
            else:
                st.write("**Status:** Failed")

            st.write("**Output:**")
            out = exec_result.get("output", "")
            st.code(out if out else "(no output)")

            if exec_result.get("error"):
                st.write("**Error:**")
                st.error(exec_result.get("error"))

            if exec_result.get("error_type"):
                st.write("**Error Type:**")
                st.code(exec_result.get("error_type"))

        # Agent history (structured)
        history = result.get("history", [])
        with st.expander("🗂️ Agent History (Debug View)", expanded=False):
            if not history:
                st.info("No history recorded.")
            else:
                for entry in history:
                    st.markdown(f"### {entry['agent']} — {entry['phase']}")
                    st.write(f"**Status:** {entry['status']}")
                    st.write(f"**Summary:** {entry['summary']}")
                    if entry.get("extra"):
                        st.write("**Details:**")
                        st.json(entry["extra"])
                    st.write(f"_Timestamp: {entry['timestamp']}_")
                    st.markdown("---")
