"""
Telegram Bot - Prompt Master AI Assistant
Send /start to begin | Use /prompt to access Prompt Builder
"""
import os
import re
import logging
from dotenv import load_dotenv
load_dotenv()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
)

from agent_system import ai_team

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# User state storage
user_states = {}  # user_id -> {chat_enabled: bool, selected_skill: str, prompt_mode: bool}

# Skills definition
SKILLS = {
    'educator': '📚 Educator - Learning & Tutorials',
    'engineer': '💻 Engineer - Code & Development',
    'debugger': '🔧 Debugger - Fix Issues & Bugs',
    'reviewer': '🔍 Reviewer - Code Review & Analysis',
    'writer': '✍️ Writer - Content & Documentation',
    'devops': '🚀 DevOps - CI/CD & Infrastructure',
    'security': '🔒 Security - Auth & Protection',
    'data': '📊 Data - Analytics & Processing',
    'business': '💼 Business - Strategy & Planning',
    'support': '🎧 Support - Help & Troubleshooting',
}

# Role definitions for prompt generation
ROLES = {
    'educator': "You are an expert educator who explains concepts clearly with practical examples.",
    'engineer': "You are a senior software engineer with expertise in multiple technologies.",
    'debugger': "You are a debugging expert who identifies and fixes code issues systematically.",
    'reviewer': "You are a code reviewer focused on quality, security, and best practices.",
    'writer': "You are a professional content writer creating clear, engaging material.",
    'devops': "You are a DevOps engineer expert in CI/CD, containers, and cloud infrastructure.",
    'security': "You are a cybersecurity expert focused on secure coding and protection.",
    'data': "You are a data analyst expert in statistics, visualization, and insights.",
    'business': "You are a business strategist helping with planning and decision making.",
    'support': "You are a technical support specialist providing clear solutions.",
}

def analyze_task(text: str) -> tuple:
    """Analyze user input and detect domain, tech stack, task type."""
    lower = text.lower()

    # Debugging patterns (Priority 1)
    debug_patterns = ['bug', 'error', 'issue', 'problem', 'fail', 'not working',
                       'kaam nahi', 'chal nahi', 'thik karo', 'sudhar', 'exception',
                       'crash', 'ruk gaya', 'band ho', 'kharab', 'galat']
    if any(p in lower for p in debug_patterns):
        return 'debugger', 'debugging', detect_tech(lower)

    # Security patterns (Priority 1)
    sec_patterns = ['security', 'auth', 'password', 'encrypt', 'jwt', 'oauth',
                   'secure', 'permission', 'hack', 'vulnerability', 'ssl', 'https']
    if any(p in lower for p in sec_patterns):
        return 'security', 'security', detect_tech(lower)

    # Review patterns (Priority 2)
    review_patterns = ['review', 'check code', 'analyze', 'audit', 'optimize',
                     'performance', 'improve', 'clean']
    if any(p in lower for p in review_patterns):
        return 'reviewer', 'review', detect_tech(lower)

    # Education patterns (Priority 2)
    edu_patterns = ['kaise', 'samjhao', 'explain', 'basics', 'kya hai', 'what is',
                   'tutorial', 'learn', 'seekho', 'samajh']
    if any(p in lower for p in edu_patterns):
        return 'educator', 'education', detect_tech(lower)

    # DevOps patterns (Priority 2)
    devops_patterns = ['ci/cd', 'pipeline', 'docker', 'kubernetes', 'deploy',
                      'server', 'cloud', 'aws', 'azure', 'linux', 'monitoring']
    if any(p in lower for p in devops_patterns):
        return 'devops', 'devops', detect_tech(lower)

    # Content patterns (Priority 2)
    content_patterns = ['blog', 'email', 'document', 'article', 'write', 'likh']
    if any(p in lower for p in content_patterns):
        return 'writer', 'content', []

    # Default to engineering
    return 'engineer', 'coding', detect_tech(lower)

def detect_tech(text: str) -> list:
    """Detect technology stack from text."""
    techs = []
    tech_map = {
        'React': ['react', 'jsx', 'tsx', 'reactjs'],
        'Python': ['python', 'python3', 'django', 'flask', 'fastapi'],
        'JavaScript': ['javascript', 'js', 'node', 'nodejs', 'express'],
        'TypeScript': ['typescript', 'ts'],
        'Docker': ['docker', 'container', 'dockerfile'],
        'AWS': ['aws', 'ec2', 's3', 'lambda', 'cloudwatch'],
        'Database': ['mysql', 'postgresql', 'mongodb', 'postgres', 'redis'],
        'Git': ['git', 'github', 'gitlab', 'commit'],
        'API': ['api', 'rest', 'graphql', 'endpoint'],
        'Frontend': ['html', 'css', 'tailwind', 'bootstrap'],
    }
    for tech, patterns in tech_map.items():
        if any(p in text for p in patterns):
            techs.append(tech)
    return techs

def detect_language(text: str) -> str:
    """Detect if input is Hindi/English."""
    hindi_pattern = re.compile(r'[\u0900-\u097F]')
    if hindi_pattern.search(text):
        return 'Hindi'
    return 'English'

def build_prompt(role: str, task_type: str, tech_stack: list, lang: str, user_input: str) -> str:
    """Build structured prompt from user input."""
    role_instruction = ROLES.get(role, ROLES['engineer'])

    prompt_parts = [
        f"## Role\n{role_instruction}",
        f"## Task Type\n{task_type.capitalize()}",
    ]

    if tech_stack:
        prompt_parts.append(f"## Tech Stack\n{', '.join(tech_stack)}")

    prompt_parts.extend([
        f"## Language\n{lang}",
        f"## User Request\n{user_input}",
        "## Output Format\nProvide clear, actionable response with examples where helpful.",
    ])

    return '\n\n'.join(prompt_parts)

def get_skill_keyboard() -> InlineKeyboardMarkup:
    """Create inline keyboard for skill selection."""
    keyboard = []
    row = []
    for i, (skill_id, skill_name) in enumerate(SKILLS.items()):
        row.append(InlineKeyboardButton(skill_name.split(' ')[0], callback_data=f"skill_{skill_id}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton("🔄 Auto-Detect", callback_data="skill_auto"),
        InlineKeyboardButton("✅ Done", callback_data="skill_done")
    ])

    return InlineKeyboardMarkup(keyboard)

def get_main_keyboard() -> InlineKeyboardMarkup:
    """Create main menu keyboard."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎯 Prompt Builder", callback_data="menu_prompt")],
        [InlineKeyboardButton("🤖 AI Chat", callback_data="menu_chat")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings")],
        [InlineKeyboardButton("📋 All Skills", callback_data="menu_skills")],
    ])

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user_id = update.effective_user.id
    user_states[user_id] = {'chat_enabled': True, 'selected_skill': None, 'prompt_mode': False}

    await update.message.reply_text(
        "🤖 *SAI Rolotech AI Bot - Prompt Master*\n\n"
        "Welcome! I can help you in Hindi/English Hinglish.\n\n"
        "🎯 *Mode Options:*\n"
        "• *AI Chat* - Direct conversation with AI team\n"
        "• *Prompt Builder* - Build structured prompts\n\n"
        "💡 Just type naturally and I'll understand!",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    await update.message.reply_text(
        "📚 *Commands:*\n\n"
        "/start - Start the bot\n"
        "/prompt - Open Prompt Builder\n"
        "/chat - Toggle AI Chat Mode\n"
        "/skill - Select your skill\n"
        "/help - Show this help\n\n"
        "💡 Just type naturally in Hindi/English!",
        parse_mode="Markdown"
    )

async def prompt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /prompt command - open Prompt Builder."""
    user_id = update.effective_user.id
    if user_id not in user_states:
        user_states[user_id] = {'chat_enabled': True, 'selected_skill': None, 'prompt_mode': True}
    else:
        user_states[user_id]['prompt_mode'] = True

    await update.message.reply_text(
        "🎯 *Prompt Builder Mode*\n\n"
        "Select a skill or I'll auto-detect from your message:",
        parse_mode="Markdown",
        reply_markup=get_skill_keyboard()
    )

async def chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /chat command - toggle chat mode."""
    user_id = update.effective_user.id
    if user_id not in user_states:
        user_states[user_id] = {'chat_enabled': True, 'selected_skill': None, 'prompt_mode': False}
    else:
        user_states[user_id]['prompt_mode'] = False

    state = user_states[user_id]
    state['chat_enabled'] = not state['chat_enabled']

    status = "ON 🟢" if state['chat_enabled'] else "OFF 🔴"
    await update.message.reply_text(f"🤖 AI Chat Mode: {status}")

async def skill_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /skill command - show skill selection."""
    await update.message.reply_text(
        "🎯 *Select Your Skill:*\n\n"
        "Choose how I should assist you:",
        parse_mode="Markdown",
        reply_markup=get_skill_keyboard()
    )

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries from inline keyboards."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if user_id not in user_states:
        user_states[user_id] = {'chat_enabled': True, 'selected_skill': None, 'prompt_mode': False}

    if data.startswith("skill_"):
        skill = data.replace("skill_", "")

        if skill == "auto":
            user_states[user_id]['selected_skill'] = None
            await query.edit_message_text(
                "🔄 *Auto-Detect Mode*\n\n"
                "I'll automatically detect the best skill based on your message.\n\n"
                "Just type your query naturally!",
                parse_mode="Markdown"
            )
        elif skill == "done":
            selected = user_states[user_id].get('selected_skill')
            if selected:
                skill_name = SKILLS.get(selected, selected).split(' ', 1)[1] if ' ' in SKILLS.get(selected, selected) else selected
                await query.edit_message_text(
                    f"✅ *Skill Selected: {skill_name}*\n\n"
                    f"Your prompts will be tailored as a {selected}. Go ahead and type your request!",
                    parse_mode="Markdown"
                )
            else:
                await query.edit_message_text(
                    "✅ *Settings Saved*\n\nGo ahead and type your request!",
                    parse_mode="Markdown"
                )
        else:
            user_states[user_id]['selected_skill'] = skill
            skill_name = SKILLS.get(skill, skill).split(' ', 1)[1] if ' ' in SKILLS.get(skill, skill) else skill
            await query.edit_message_text(
                f"✅ *Skill Selected: {skill_name}*\n\n"
                f"Now type your request and I'll respond as a {skill}!",
                parse_mode="Markdown",
                reply_markup=get_skill_keyboard()
            )

    elif data.startswith("menu_"):
        menu = data.replace("menu_", "")

        if menu == "prompt":
            user_states[user_id]['prompt_mode'] = True
            await query.edit_message_text(
                "🎯 *Prompt Builder Mode*\n\n"
                "Select a skill or I'll auto-detect:",
                parse_mode="Markdown",
                reply_markup=get_skill_keyboard()
            )
        elif menu == "chat":
            user_states[user_id]['prompt_mode'] = False
            await query.edit_message_text(
                "🤖 *AI Chat Mode*\n\n"
                "Direct chat with AI team enabled!",
                parse_mode="Markdown"
            )
        elif menu == "settings":
            state = user_states[user_id]
            chat_status = "🟢 ON" if state.get('chat_enabled', True) else "🔴 OFF"
            skill = state.get('selected_skill', 'Auto')

            await query.edit_message_text(
                "⚙️ *Settings*\n\n"
                f"• AI Chat: {chat_status}\n"
                f"• Skill: {skill}\n"
                f"• Mode: {'Prompt Builder' if state.get('prompt_mode') else 'AI Chat'}",
                parse_mode="Markdown"
            )
        elif menu == "skills":
            skills_text = "📋 *All Skills:*\n\n"
            for sid, sname in SKILLS.items():
                skills_text += f"{sname}\n"
            await query.edit_message_text(skills_text, parse_mode="Markdown")

async def handle_message(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages."""
    user_id = update.effective_user.id
    user_message = update.message.text

    if user_id not in user_states:
        user_states[user_id] = {'chat_enabled': True, 'selected_skill': None, 'prompt_mode': False}

    state = user_states[user_id]

    # Detect language
    lang = detect_language(user_message)

    # Analyze task
    role, task_type, tech_stack = analyze_task(user_message)

    # Use selected skill if set
    if state.get('selected_skill'):
        role = state['selected_skill']

    # Build prompt
    prompt = build_prompt(role, task_type, tech_stack, lang, user_message)

    # Check if prompt mode or chat mode
    if state.get('prompt_mode'):
        # Show generated prompt
        tech_str = f"\n📦 Tech: {', '.join(tech_stack)}" if tech_stack else ""
        await update.message.reply_text(
            f"🎯 *Prompt Generated*\n\n"
            f"👤 Skill: {role.capitalize()}\n"
            f"📋 Task: {task_type}{tech_str}\n"
            f"🌐 Lang: {lang}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{prompt}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"_Sending to AI team..._",
            parse_mode="Markdown"
        )

    # Send to AI team
    await update.message.reply_text("🤔 Processing...", parse_mode="Markdown")

    try:
        response = await ai_team.arun(prompt)
        await update.message.reply_text(f"🤖 {response}")
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")

def main():
    """Start the Telegram bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not found in .env")
        print("Get your token from @BotFather on Telegram")
        return

    print("🚀 Starting Prompt Master Telegram Bot...")

    app = Application.builder().token(token).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("prompt", prompt_command))
    app.add_handler(CommandHandler("chat", chat_command))
    app.add_handler(CommandHandler("skill", skill_command))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot ready! Press Ctrl+C to stop")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()