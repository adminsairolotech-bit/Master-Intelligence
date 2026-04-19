"""
SAI Rolotech - Hermes Agent Web Interface
Streamlit App
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from hermes_agent import HermesAgent

st.set_page_config(
    page_title="Hermes AI - SAI Rolotech",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if "hermes" not in st.session_state:
    st.session_state.hermes = HermesAgent(user_id="sai")
    st.session_state.messages = []

if "memory" not in st.session_state:
    st.session_state.memory = []

st.title("🤖 Hermes AI Agent")
st.caption("Persistent Memory • Self-Improving • Multi-Model")

# Sidebar
with st.sidebar:
    st.header("Settings")

    model = st.selectbox(
        "AI Model",
        ["gemini", "fast", "smart", "heavy"],
        format_func=lambda x: {
            "gemini": "Gemini 2.5 Flash (FREE)",
            "fast": "Groq Llama (FAST)",
            "smart": "DeepSeek V3 (Smart)",
            "heavy": "Claude Sonnet (Heavy)"
        }[x]
    )

    st.divider()

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    if st.button("🧠 View Memory"):
        memory = st.session_state.hermes.memory.get_context()
        st.text_area("Stored Memory", memory, height=200)

# Main chat
col1, col2 = st.columns([3, 1])

with col1:
    # Display messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input
    if prompt := st.chat_input("Ask Hermes..."):
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.hermes.chat(prompt, model=model)
                st.markdown(response)

        # Save message
        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })

with col2:
    st.header("Memory")
    st.caption("Hermes remembers!")

    # Quick facts
    facts = st.session_state.hermes.memory.facts.get("facts", {})
    if facts:
        for key, val in list(facts.items())[-5:]:
            st.info(f"**{key}**: {val.get('value', '')[:50]}")
    else:
        st.text("No memories yet.\nStart chatting!")

    st.divider()

    st.header("Learnings")
    learned = st.session_state.hermes.memory.facts.get("learned", [])
    if learned:
        for item in learned[-3:]:
            st.write(f"• {item.get('text', '')[:60]}...")
    else:
        st.text("None yet")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: gray;">
    SAI Rolotech AI • Hermes Agent<br>
    <small>Memory persists across sessions</small>
</div>
""", unsafe_allow_html=True)
