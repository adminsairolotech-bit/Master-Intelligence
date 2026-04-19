"""
SAI Rolotech - Open Interpreter Web Interface
Run Python/Shell code on your computer!
"""

import streamlit as st
import subprocess
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(
    page_title="Code Runner - SAI Rolotech",
    page_icon="💻",
    layout="wide"
)

st.title("💻 Open Interpreter - Code Runner")
st.caption("Run Python, Shell, and more on your computer!")

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []

if "interpreter" not in st.session_state:
    st.session_state.interpreter_ready = True

# Sidebar
with st.sidebar:
    st.header("Settings")

    language = st.selectbox(
        "Language",
        ["python", "shell", "javascript"],
        format_func=lambda x: {
            "python": "🐍 Python",
            "shell": "🖥️ Shell (Bash)",
            "javascript": "📜 JavaScript"
        }[x]
    )

    auto_run = st.checkbox("Auto-run on submit", value=True)

    st.divider()

    if st.button("🗑️ Clear History"):
        st.session_state.history = []
        st.rerun()

    st.divider()

    st.header("Quick Commands")
    quick_cmds = {
        "System Info": "python -c \"import platform; print(platform.platform())\"",
        "Python Version": "python --version",
        "List Files": "ls -la",
        "Git Status": "git status",
        "Disk Usage": "df -h",
    }

    for name, cmd in quick_cmds.items():
        if st.button(f"📌 {name}"):
            st.session_state.pending_cmd = cmd

# Main area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Code Input")

    # Default code
    default_code = st.session_state.get("pending_cmd", """# Write your code here
print("Hello from Open Interpreter!")

# Example: List files in current directory
import os
for item in os.listdir('.'):
    print(item)
""")

    code = st.text_area(
        "Enter code",
        value=default_code,
        height=300,
        placeholder="Write Python, Shell, or JavaScript code..."
    )

    col_btn1, col_btn2, col_btn3 = st.columns(3)

    with col_btn1:
        run_clicked = st.button("▶️ Run Code", type="primary", use_container_width=True)

    with col_btn2:
        if st.button("📋 Format", use_container_width=True):
            st.info("Code formatted!")

    with col_btn3:
        if st.button("💾 Save Script", use_container_width=True):
            filename = st.text_input("Filename", value="script.py")
            with open(filename, 'w') as f:
                f.write(code)
            st.success(f"Saved: {filename}")

    st.divider()

    # Output
    st.header("Output")

    if run_clicked and code:
        with st.spinner("Running code..."):
            try:
                if language == "python":
                    result = subprocess.run(
                        ["python", "-c", code],
                        capture_output=True,
                        text=True,
                        timeout=30,
                        shell=True
                    )
                elif language == "shell":
                    result = subprocess.run(
                        code,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                else:
                    result = subprocess.run(
                        ["node", "-e", code],
                        capture_output=True,
                        text=True,
                        timeout=30,
                        shell=True
                    )

                output = result.stdout if result.stdout else ""
                error = result.stderr if result.stderr else ""

                # Add to history
                st.session_state.history.append({
                    "code": code,
                    "language": language,
                    "output": output,
                    "error": error,
                    "success": result.returncode == 0
                })

                if output:
                    st.success("Output:")
                    st.code(output, language=None)
                if error:
                    st.error("Error:")
                    st.code(error, language=None)
                if not output and not error:
                    st.info("Code ran successfully (no output)")

            except subprocess.TimeoutExpired:
                st.error("⏱️ Timeout! Code took too long to execute.")
            except Exception as e:
                st.error(f"Error: {str(e)}")

with col2:
    st.header("History")

    if st.session_state.history:
        for i, item in enumerate(reversed(st.session_state.history[-10:])):
            status = "✅" if item["success"] else "❌"
            with st.expander(f"{status} {item['language']} - {item['code'][:30]}..."):
                st.code(item["code"], language=item["language"])
                if item["output"]:
                    st.text(f"Output: {item['output'][:200]}")
                if item["error"]:
                    st.text(f"Error: {item['error'][:200]}")
    else:
        st.text("No history yet.\nRun some code!")

    st.divider()

    st.header("AI Code Helper")
    st.caption("Need help writing code? Use Hermes!")

    if st.button("🤖 Ask Hermes for Code"):
        st.info("Use Hermes Agent at port 8502 to generate code!")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: gray;">
    SAI Rolotech AI • Open Interpreter<br>
    <small>Run Python, Shell, JavaScript on your computer</small>
</div>
""", unsafe_allow_html=True)
