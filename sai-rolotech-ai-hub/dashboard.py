"""
SAI Rolotech AI Hub - Complete Dashboard
Streamlit Dashboard
"""

import streamlit as st
import requests
import time

st.set_page_config(
    page_title="SAI Rolotech AI Hub",
    page_icon="🤖",
    layout="wide"
)

# API Base
API_BASE = "http://localhost:8505"

st.title("🤖 SAI Rolotech AI Hub - Dashboard")
st.markdown("---")

# ==================== SIDEBAR ====================

with st.sidebar:
    st.header("Settings")

    # Check API status
    try:
        response = requests.get(f"{API_BASE}/", timeout=2)
        if response.status_code == 200:
            st.success("✅ AI Hub Connected")
        else:
            st.error("❌ API Error")
    except:
        st.error("❌ AI Hub Offline")
        st.info("Start with: `python main.py`")

    st.markdown("---")

    # Quick actions
    st.header("Quick Actions")

    if st.button("📋 Refresh Data"):
        st.rerun()

    st.markdown("---")

    # API endpoints
    st.header("API Endpoints")
    st.code(f"""
POST {API_BASE}/chat
GET  {API_BASE}/crm/stats
POST {API_BASE}/crm/lead
GET  {API_BASE}/crm/leads
POST {API_BASE}/memory
GET  {API_BASE}/memory/{{user_id}}
POST {API_BASE}/run
""")

# ==================== MAIN CONTENT ====================

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Stats", "📋 Leads", "💬 Chat", "🤖 Models", "🔧 Tools"])

# ==================== STATS TAB ====================

with tab1:
    st.header("Business Statistics")

    try:
        response = requests.get(f"{API_BASE}/crm/stats")
        if response.status_code == 200:
            stats = response.json()

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Leads", stats.get("total_leads", 0))

            with col2:
                st.metric("New", stats.get("new", 0))

            with col3:
                st.metric("Contacted", stats.get("contacted", 0))

            with col4:
                st.metric("Won", stats.get("won", 0))

        else:
            st.error("Failed to load stats")

    except Exception as e:
        st.error(f"Error: {e}")

# ==================== LEADS TAB ====================

with tab2:
    st.header("Lead Management")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Add New Lead")

        with st.form("add_lead"):
            name = st.text_input("Name")
            mobile = st.text_input("Mobile")
            email = st.text_input("Email (optional)")
            source = st.selectbox("Source", ["telegram", "facebook", "website", "call", "referral"])

            if st.form_submit_button("Add Lead"):
                try:
                    response = requests.post(
                        f"{API_BASE}/crm/lead",
                        json={"name": name, "mobile": mobile, "email": email, "source": source}
                    )
                    if response.status_code == 200:
                        st.success("✅ Lead created!")
                    else:
                        st.error("❌ Failed")
                except:
                    st.error("❌ API not running")

    with col2:
        st.subheader("All Leads")

        try:
            response = requests.get(f"{API_BASE}/crm/leads")
            if response.status_code == 200:
                leads = response.json().get("leads", [])

                if leads:
                    for lead in leads:
                        with st.expander(f"📋 {lead['name']} - {lead['mobile']}"):
                            st.write(f"**Stage:** {lead['stage']}")
                            st.write(f"**Source:** {lead['source']}")
                            st.write(f"**Created:** {lead['created_at']}")
                else:
                    st.info("No leads yet")
            else:
                st.error("Failed to load leads")

        except Exception as e:
            st.error(f"Error: {e}")

# ==================== CHAT TAB ====================

with tab3:
    st.header("Chat with Hermes AI")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Type your message..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = requests.post(
                        f"{API_BASE}/chat",
                        json={"user_id": 1, "message": prompt},
                        timeout=30
                    )

                    if response.status_code == 200:
                        result = response.json()
                        ai_response = result.get("response", "No response")
                        st.markdown(ai_response)
                        st.session_state.messages.append({"role": "assistant", "content": ai_response})
                    else:
                        st.error("Failed to get response")

                except Exception as e:
                    st.error(f"Error: {e}")

    # Clear chat
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []

# ==================== MODELS TAB ====================

with tab4:
    st.header("AI Models")

    models = [
        ("Gemini 2.5 Flash", "google/gemini-2.5-flash", "FREE", "⚡⚡⚡⚡", "Fast daily tasks"),
        ("DeepSeek V3", "deepseek/deepseek-chat-v3", "FREE", "🧠🧠🧠", "Coding & reasoning"),
        ("Groq Llama 3.3", "llama-3.3-70b-versatile", "FREE", "⚡⚡⚡⚡⚡", "Ultra fast"),
        ("Claude Sonnet", "claude-sonnet-4-6", "PAID", "💎💎💎💎", "Complex tasks"),
        ("Qwen 72B", "qwen/qwen2.5-72b-instruct", "FREE", "🧠🧠🧠🧠", "Large model"),
        ("Mistral Nemo", "mistralai/mistral-nemo", "FREE", "⚡⚡⚡", "Balanced"),
    ]

    for model in models:
        name, model_id, cost, rating, use_case = model

        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.write(f"**{name}**")
            st.caption(f"{model_id}")

        with col2:
            color = "green" if cost == "FREE" else "orange"
            st.markdown(f"<span style='color:{color}'>{cost}</span>", unsafe_allow_html=True)

        with col3:
            st.write(rating)

        st.write(f"Best for: {use_case}")
        st.markdown("---")

# ==================== TOOLS TAB ====================

with tab5:
    st.header("Tools & Services")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🧠 Hermes AI")
        st.write("AI Brain + Memory")
        st.write(f"API: {API_BASE}/chat")

        if st.button("Test Hermes"):
            try:
                response = requests.post(
                    f"{API_BASE}/chat",
                    json={"user_id": 1, "message": "Hello!"}
                )
                if response.status_code == 200:
                    st.success("Hermes working!")
                else:
                    st.error("Failed")
            except:
                st.error("API not running")

    with col2:
        st.subheader("💻 Interpreter")
        st.write("Run code safely")
        st.write(f"API: {API_BASE}/run")

        code = st.text_area("Python Code", value="print('Hello from Interpreter!')")

        if st.button("Run Code"):
            try:
                response = requests.post(
                    f"{API_BASE}/run",
                    json={"code": code, "language": "python"}
                )
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        st.success(f"Output: {result.get('output', 'No output')}")
                    else:
                        st.error(f"Error: {result.get('error', 'Unknown')}")
            except:
                st.error("API not running")

    st.markdown("---")

    # n8n workflows
    st.subheader("🔗 n8n Workflows")

    workflows = [
        ("Lead Creation", "POST /webhook/lead-create"),
        ("Daily Report", "Every morning 9 AM"),
        ("Follow-up", "POST /webhook/followup-trigger"),
        ("Task Scheduler", "POST /webhook/task-schedule"),
    ]

    for name, desc in workflows:
        st.write(f"• **{name}**: {desc}")

    st.markdown("---")

    # System status
    st.subheader("📊 System Status")

    services = [
        ("AI Hub API", f"{API_BASE}", "8505"),
        ("OpenClaw", "http://localhost:18789", "18789"),
        ("n8n", "http://localhost:5678", "5678"),
        ("Telegram Bot", "telegram_bot.py", "Bot"),
    ]

    for name, url, port in services:
        status = "✅" if requests.get(f"{API_BASE}/health", timeout=1).status_code == 200 else "❌"
        st.write(f"{status} **{name}** ({port})")

# ==================== FOOTER ====================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray;">
    SAI Rolotech AI Hub - Production Ready<br>
    <small>
        Hermes Brain | OpenClaw | n8n | Interpreter<br>
        Built with ❤️
    </small>
</div>
""", unsafe_allow_html=True)
