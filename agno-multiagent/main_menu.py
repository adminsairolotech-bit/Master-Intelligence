"""
SAI Rolotech AI - Main Dashboard
All AI Tools in One Place
"""

import streamlit as st
import webbrowser
import subprocess
import os

st.set_page_config(
    page_title="SAI Rolotech AI Hub",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    text-align: center;
    padding: 1rem;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.tool-card {
    padding: 1.5rem;
    border-radius: 1rem;
    background: #1a1a2e;
    border: 1px solid #333;
    text-align: center;
    transition: transform 0.3s;
}
.tool-card:hover {
    transform: scale(1.02);
    border-color: #667eea;
}
.tool-name {
    font-size: 1.5rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
}
.tool-desc {
    color: #888;
    font-size: 0.9rem;
}
.status-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 1rem;
    font-size: 0.8rem;
    margin-top: 0.5rem;
}
.status-running {
    background: #10b981;
    color: white;
}
.status-stopped {
    background: #ef4444;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🤖 SAI ROLOTECH AI HUB</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #888;">Complete AI Development Environment</p>', unsafe_allow_html=True)

st.divider()

# ==================== AI AGENTS SECTION ====================

st.header("🤖 AI Agents")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="tool-card">
        <div class="tool-name">🤖 Hermes Agent</div>
        <div class="tool-desc">Persistent Memory AI<br>Remembers everything</div>
        <span class="status-badge status-running">✅ Running</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🌐 Open Hermes", key="open_hermes"):
        webbrowser.open("http://localhost:8502")
    if st.button("📝 View Code", key="view_hermes"):
        st.code(open("hermes_agent.py").read(), language="python")

with col2:
    st.markdown("""
    <div class="tool-card">
        <div class="tool-name">💻 Open Interpreter</div>
        <div class="tool-desc">Run Python/Shell code<br>On your computer</div>
        <span class="status-badge status-running">✅ Running</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🌐 Open Interpreter", key="open_interp"):
        webbrowser.open("http://localhost:8503")
    if st.button("📝 View Code", key="view_interp"):
        st.code(open("interpreter_web.py").read(), language="python")

with col3:
    st.markdown("""
    <div class="tool-card">
        <div class="tool-name">⚡ Fast Agent</div>
        <div class="tool-desc">Groq Llama 3.3<br>Ultra fast responses</div>
        <span class="status-badge status-running">✅ Ready</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("⚡ Test Fast Agent", key="test_fast"):
        with st.spinner("Testing..."):
            st.info("Use agent_system.py in terminal")

# ==================== OPENCLAW SECTION ====================

st.divider()
st.header("🔗 Integrations")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="tool-card">
        <div class="tool-name">🦅 OpenClaw</div>
        <div class="tool-desc">AI Gateway<br>Telegram Bot</div>
        <span class="status-badge status-running">✅ Live</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🌐 OpenClaw", key="open_oc"):
        webbrowser.open("http://localhost:18789")

with col2:
    st.markdown("""
    <div class="tool-card">
        <div class="tool-name">🔗 n8n</div>
        <div class="tool-desc">Workflow Automation<br>Connect everything</div>
        <span class="status-badge status-running">✅ Ready</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🌐 n8n", key="open_n8n"):
        webbrowser.open("http://localhost:5678")

with col3:
    st.markdown("""
    <div class="tool-card">
        <div class="tool-name">📊 CRM</div>
        <div class="tool-desc">SAI Rolotech CRM<br>Leads & Products</div>
        <span class="status-badge status-running">✅ Ready</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🌐 CRM", key="open_crm"):
        webbrowser.open("http://localhost:3000")

with col4:
    st.markdown("""
    <div class="tool-card">
        <div class="tool-name">🎨 Node-RED</div>
        <div class="tool-desc">Flow Editor<br>IoT & Automation</div>
        <span class="status-badge status-running">✅ Ready</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🌐 Node-RED", key="open_nodered"):
        webbrowser.open("http://localhost:1880")

# ==================== AI MODELS ====================

st.divider()
st.header("🧠 AI Models Available")

models_data = [
    ("Gemini 2.5 Flash", "google/gemini-2.5-flash", "FREE", "⚡⚡⚡⚡"),
    ("DeepSeek V3", "deepseek/deepseek-chat-v3", "FREE", "🧠🧠🧠"),
    ("Groq Llama 3.3", "llama-3.3-70b-versatile", "FREE", "⚡⚡⚡⚡⚡"),
    ("Claude 4.7 Opus", "claude-opus-4-7", "PAID", "💎💎💎💎💎"),
    ("Qwen 72B", "qwen/qwen2.5-72b-instruct", "FREE", "🧠🧠🧠🧠"),
    ("Mistral Nemo", "mistralai/mistral-nemo", "FREE", "⚡⚡⚡"),
]

for i in range(0, len(models_data), 3):
    cols = st.columns(3)
    for j, model in enumerate(models_data[i:i+3]):
        with cols[j]:
            name, model_id, cost, rating = model
            st.markdown(f"""
            <div class="tool-card">
                <div class="tool-name">{name}</div>
                <div class="tool-desc">{model_id}</div>
                <span style="color: {'#10b981' if cost == 'FREE' else '#f59e0b'};">{cost}</span>
                <div style="margin-top: 0.5rem;">{rating}</div>
            </div>
            """, unsafe_allow_html=True)

# ==================== FRAMEWORKS ====================

st.divider()
st.header("🛠️ AI Frameworks")

frameworks = [
    ("LangGraph", "1.1.6", "Agent workflows"),
    ("LangChain", "1.2.15", "Chains & prompts"),
    ("CrewAI", "1.14.1", "Multi-agent teams"),
    ("Open Interpreter", "0.4.3", "Code execution"),
    ("Agno", "2.5.17", "Multi-agent system"),
    ("DeepEval", "3.9.7", "Testing & evaluation"),
]

for fw, ver, desc in frameworks:
    st.markdown(f"**{fw}** v{ver} - {desc}")

# ==================== QUICK ACTIONS ====================

st.divider()
st.header("⚡ Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🆕 New Hermes Chat", use_container_width=True):
        st.info("Chat at Hermes Agent (port 8502)")

with col2:
    if st.button("💻 Run Code", use_container_width=True):
        webbrowser.open("http://localhost:8503")

with col3:
    if st.button("📁 Open Project", use_container_width=True):
        os.startfile(os.path.dirname(__file__))

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: gray; padding: 1rem;">
    SAI Rolotech AI Hub • Built with Streamlit<br>
    <small>All AI tools in one place</small>
</div>
""", unsafe_allow_html=True)
