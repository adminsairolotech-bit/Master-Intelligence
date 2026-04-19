"""
Telegram Bot - Prompt Master AI Assistant with Live Screen
Send /start to begin | Use /prompt to access Prompt Builder | Use /screen for live monitoring
"""
import os
import re
import logging
import asyncio
import base64
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
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
user_states = {}  # user_id -> {chat_enabled, selected_skill, prompt_mode, screen_monitoring}

# Screen monitoring intervals
screen_intervals = {}

# Skills definition
SKILLS = {
    'educator': '📚 Educator',
    'engineer': '💻 Engineer',
    'debugger': '🔧 Debugger',
    'reviewer': '🔍 Reviewer',
    'writer': '✍️ Writer',
    'devops': '🚀 DevOps',
    'security': '🔒 Security',
    'data': '📊 Data',
    'business': '💼 Business',
    'support': '🎧 Support',
}

# Role definitions
ROLES = {
    'educator': "You are an expert educator who explains concepts clearly.",
    'engineer': "You are a senior software engineer with expertise in multiple technologies.",
    'debugger': "You are a debugging expert who identifies and fixes code issues.",
    'reviewer': "You are a code reviewer focused on quality and best practices.",
    'writer': "You are a professional content writer creating clear material.",
    'devops': "You are a DevOps engineer expert in CI/CD and infrastructure.",
    'security': "You are a cybersecurity expert focused on protection.",
    'data': "You are a data analyst expert in statistics and insights.",
    'business': "You are a business strategist helping with planning.",
    'support': "You are a technical support specialist.",
}

def take_screenshot() -> str | None:
    """Take screenshot and return file path."""
    try:
        import mss
        with mss.mss() as sct:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            sct.shot(output=filename)
            return filename
    except ImportError:
        # Fallback using PIL
        try:
            from PIL import ImageGrab
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            img = ImageGrab.grab()
            img.save(filename)
            return filename
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            return None
    except Exception as e:
        logger.error(f"Screenshot error: {e}")
        return None

def get_system_info() -> str:
    """Get current system information."""
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        return (
            f"💻 *System Status*\n\n"
            f"🔲 CPU: {cpu}%\n"
            f"🧠 RAM: {mem.percent}% ({mem.used // (1024**2)}MB / {mem.total // (1024**2)}MB)\n"
            f"💾 Disk: {disk.percent}% used"
        )
    except ImportError:
        return "💻 *System Info*\n\n(psutil not installed)"
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

def analyze_task(text: str) -> tuple:
    """Analyze user input and detect domain, tech stack."""
    lower = text.lower()

    # Priority 1: Debugging
    debug_patterns = ['bug', 'error', 'issue', 'problem', 'fail', 'not working',
                       'kaam nahi', 'chal nahi', 'thik karo', 'exception', 'crash']
    if any(p in lower for p in debug_patterns):
        return 'debugger', 'debugging', detect_tech(lower)

    # Priority 1: Security
    sec_patterns = ['security', 'auth', 'password', 'jwt', 'oauth', 'vulnerability']
    if any(p in lower for p in sec_patterns):
        return 'security', 'security', detect_tech(lower)

    # Priority 2: Review
    review_patterns = ['review', 'analyze', 'audit', 'optimize', 'performance']
    if any(p in lower for p in review_patterns):
        return 'reviewer', 'review', detect_tech(lower)

    # Priority 2: Education
    edu_patterns = ['kaise', 'samjhao', 'explain', 'basics', 'kya hai', 'what is', 'tutorial']
    if any(p in lower for p in edu_patterns):
        return 'educator', 'education', detect_tech(lower)

    # Priority 2: DevOps
    devops_patterns = ['ci/cd', 'docker', 'kubernetes', 'deploy', 'server', 'cloud', 'aws']
    if any(p in lower for p in devops_patterns):
        return 'devops', 'devops', detect_tech(lower)

    # Priority 2: Content
    content_patterns = ['blog', 'email', 'document', 'article', 'write']
    if any(p in lower for p in content_patterns):
        return 'writer', 'content', []

    return 'engineer', 'coding', detect_tech(lower)

def detect_tech(text: str) -> list:
    """Detect technology stack."""
    techs = []
    tech_map = {
        'React': ['react', 'jsx', 'tsx'],
        'Python': ['python', 'django', 'flask', 'fastapi'],
        'JavaScript': ['javascript', 'js', 'node', 'express'],
        'Docker': ['docker', 'container'],
        'AWS': ['aws', 'ec2', 's3', 'lambda'],
        'Database': ['mysql', 'postgresql', 'mongodb', 'redis'],
    }
    for tech, patterns in tech_map.items():
        if any(p in text for p in patterns):
            techs.append(tech)
    return techs

def detect_language(text: str) -> str:
    """Detect Hindi/English."""
    return 'Hindi' if re.search(r'[\u0900-\u097F]', text) else 'English'

def build_prompt(role: str, task_type: str, tech_stack: list, lang: str, user_input: str) -> str:
    """Build structured prompt."""
    prompt_parts = [
        f"## Role\n{ROLES.get(role, ROLES['engineer'])}",
        f"## Task Type\n{task_type.capitalize()}",
    ]
    if tech_stack:
        prompt_parts.append(f"## Tech Stack\n{', '.join(tech_stack)}")
    prompt_parts.extend([
        f"## Language\n{lang}",
        f"## User Request\n{user_input}",
        "## Output\nProvide clear, actionable response.",
    ])
    return '\n\n'.join(prompt_parts)

def get_skill_keyboard() -> InlineKeyboardMarkup:
    """Create skill selection keyboard."""
    keyboard = []
    items = list(SKILLS.items())
    for i in range(0, len(items), 2):
        row = [InlineKeyboardButton(name, callback_data=f"skill_{sid}") for sid, name in items[i:i+2]]
        keyboard.append(row)
    keyboard.append([
        InlineKeyboardButton("🔄 Auto", callback_data="skill_auto"),
        InlineKeyboardButton("✅ Done", callback_data="skill_done")
    ])
    return InlineKeyboardMarkup(keyboard)

def get_main_keyboard() -> InlineKeyboardMarkup:
    """Main menu keyboard."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎯 Prompt Builder", callback_data="menu_prompt")],
        [InlineKeyboardButton("📸 Take Screenshot", callback_data="menu_screenshot")],
        [InlineKeyboardButton("💻 Live Monitor", callback_data="menu_monitor")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings")],
    ])

def get_monitor_keyboard() -> InlineKeyboardMarkup:
    """Screen monitoring controls."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📸 Snap", callback_data="monitor_snap")],
        [InlineKeyboardButton("▶️ Start 5s", callback_data="monitor_start_5")],
        [InlineKeyboardButton("⏹️ Stop", callback_data="monitor_stop")],
        [InlineKeyboardButton("🔄 Refresh", callback_data="monitor_refresh")],
    ])

async def start_command(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """Handle /start."""
    user_id = update.effective_user.id
    user_states[user_id] = {'chat_enabled': True, 'selected_skill': None, 'prompt_mode': False, 'monitoring': False}

    await update.message.reply_text(
        "🤖 *SAI Rolotech AI Bot - Prompt Master*\n\n"
        "🎯 *Features:*\n"
        "• Prompt Builder - Build structured prompts\n"
        "• AI Chat - Talk to AI team\n"
        "• 📸 Screenshot - Capture screen\n"
        "• 💻 Live Monitor - Watch screen live\n\n"
        "💡 Type in Hindi/English naturally!",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )

async def help_command(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """Handle /help."""
    await update.message.reply_text(
        "📚 *Commands:*\n\n"
        "/start - Welcome menu\n"
        "/prompt - Prompt Builder\n"
        "/screen - Take screenshot\n"
        "/live - Live monitor (5s)\n"
        "/info - System info\n"
        "/chat - Toggle AI Chat\n"
        "/skill - Select skill\n"
        "/stop - Stop monitoring",
        parse_mode="Markdown"
    )

async def screen_command(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """Handle /screen - take screenshot."""
    user_id = update.effective_user.id
    await update.message.reply_text("📸 Taking screenshot...")

    filename = take_screenshot()
    if filename and os.path.exists(filename):
        try:
            with open(filename, 'rb') as f:
                await update.message.reply_photo(photo=f, caption=f"📸 Screenshot {datetime.now().strftime('%H:%M:%S')}")
            os.remove(filename)
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    else:
        await update.message.reply_text("❌ Could not take screenshot. Install mss: `pip install mss`")

async def live_command(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """Handle /live - start live monitoring."""
    user_id = update.effective_user.id

    if user_id not in user_states:
        user_states[user_id] = {'chat_enabled': True, 'selected_skill': None, 'prompt_mode': False, 'monitoring': False}

    user_states[user_id]['monitoring'] = True

    await update.message.reply_text(
        "💻 *Live Screen Monitor*\n\n"
        "Taking 5 screenshots over 5 seconds...\n"
        "Use /stop to cancel.",
        parse_mode="Markdown"
    )

    # Take 5 screenshots with 1 second interval
    for i in range(5):
        if not user_states.get(user_id, {}).get('monitoring', False):
            break

        filename = take_screenshot()
        if filename and os.path.exists(filename):
            try:
                with open(filename, 'rb') as f:
                    await update.message.reply_photo(
                        photo=f,
                        caption=f"📸 Frame {i+1}/5 - {datetime.now().strftime('%H:%M:%S')}"
                    )
                os.remove(filename)
            except:
                pass

        await asyncio.sleep(1)

    user_states[user_id]['monitoring'] = False
    await update.message.reply_text("✅ Live monitor complete!")

async def stop_command(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """Handle /stop - stop monitoring."""
    user_id = update.effective_user.id
    if user_id in user_states:
        user_states[user_id]['monitoring'] = False
    await update.message.reply_text("⏹️ Monitoring stopped.")

async def info_command(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """Handle /info - system info."""
    info = get_system_info()
    await update.message.reply_text(info, parse_mode="Markdown")

async def prompt_command(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """Handle /prompt."""
    user_id = update.effective_user.id
    if user_id not in user_states:
        user_states[user_id] = {'chat_enabled': True, 'selected_skill': None, 'prompt_mode': True, 'monitoring': False}
    else:
        user_states[user_id]['prompt_mode'] = True

    await update.message.reply_text(
        "🎯 *Prompt Builder*\n\nSelect a skill or I'll auto-detect:",
        parse_mode="Markdown",
        reply_markup=get_skill_keyboard()
    )

async def chat_command(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """Handle /chat toggle."""
    user_id = update.effective_user.id
    if user_id not in user_states:
        user_states[user_id] = {'chat_enabled': True, 'selected_skill': None, 'prompt_mode': False, 'monitoring': False}
    else:
        user_states[user_id]['prompt_mode'] = False

    state = user_states[user_id]
    state['chat_enabled'] = not state['chat_enabled']
    status = "ON 🟢" if state['chat_enabled'] else "OFF 🔴"
    await update.message.reply_text(f"🤖 AI Chat: {status}")

async def skill_command(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """Handle /skill."""
    await update.message.reply_text(
        "🎯 *Select Skill:*",
        parse_mode="Markdown",
        reply_markup=get_skill_keyboard()
    )

async def callback_handler(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard callbacks."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if user_id not in user_states:
        user_states[user_id] = {'chat_enabled': True, 'selected_skill': None, 'prompt_mode': False, 'monitoring': False}

    # Skill selection
    if data.startswith("skill_"):
        skill = data.replace("skill_", "")

        if skill == "auto":
            user_states[user_id]['selected_skill'] = None
            await query.edit_message_text("🔄 *Auto-Detect* enabled. Type your request!", parse_mode="Markdown")
        elif skill == "done":
            selected = user_states[user_id].get('selected_skill')
            if selected:
                await query.edit_message_text(f"✅ Skill: {SKILLS.get(selected, selected)}. Type your request!", parse_mode="Markdown")
            else:
                await query.edit_message_text("✅ Ready! Type your request.", parse_mode="Markdown")
        else:
            user_states[user_id]['selected_skill'] = skill
            await query.edit_message_text(
                f"✅ Skill: {SKILLS.get(skill, skill)}. Type your request!",
                parse_mode="Markdown",
                reply_markup=get_skill_keyboard()
            )

    # Menu actions
    elif data.startswith("menu_"):
        menu = data.replace("menu_", "")

        if menu == "prompt":
            user_states[user_id]['prompt_mode'] = True
            await query.edit_message_text(
                "🎯 *Prompt Builder*\n\nSelect skill:",
                parse_mode="Markdown",
                reply_markup=get_skill_keyboard()
            )
        elif menu == "screenshot":
            await query.edit_message_text("📸 Taking screenshot...")
            filename = take_screenshot()
            if filename and os.path.exists(filename):
                with open(filename, 'rb') as f:
                    await query.message.reply_photo(photo=f, caption=f"📸 {datetime.now().strftime('%H:%M:%S')}")
                os.remove(filename)
            else:
                await query.edit_message_text("❌ Screenshot failed. Install mss.", parse_mode="Markdown")

        elif menu == "monitor":
            await query.edit_message_text(
                "💻 *Live Monitor*\n\nControls:",
                parse_mode="Markdown",
                reply_markup=get_monitor_keyboard()
            )

        elif menu == "settings":
            state = user_states[user_id]
            skill = state.get('selected_skill', 'Auto')
            chat = "🟢" if state.get('chat_enabled', True) else "🔴"
            await query.edit_message_text(
                f"⚙️ *Settings*\n\n• Chat: {chat}\n• Skill: {skill}",
                parse_mode="Markdown"
            )

    # Monitor controls
    elif data.startswith("monitor_"):
        action = data.replace("monitor_", "")

        if action == "snap":
            await query.edit_message_text("📸 Capturing...")
            filename = take_screenshot()
            if filename and os.path.exists(filename):
                with open(filename, 'rb') as f:
                    await query.message.reply_photo(photo=f, caption=f"📸 {datetime.now().strftime('%H:%M:%S')}")
                os.remove(filename)
            await query.edit_message_text("💻 *Monitor*", parse_mode="Markdown", reply_markup=get_monitor_keyboard())

        elif action == "start_5":
            user_states[user_id]['monitoring'] = True
            await query.edit_message_text("💻 Taking 5 frames...")
            for i in range(5):
                if not user_states.get(user_id, {}).get('monitoring', False):
                    break
                filename = take_screenshot()
                if filename and os.path.exists(filename):
                    with open(filename, 'rb') as f:
                        await query.message.reply_photo(photo=f, caption=f"Frame {i+1}/5")
                    os.remove(filename)
                await asyncio.sleep(1)
            user_states[user_id]['monitoring'] = False
            await query.edit_message_text("✅ Done!", parse_mode="Markdown", reply_markup=get_monitor_keyboard())

        elif action == "stop":
            user_states[user_id]['monitoring'] = False
            await query.edit_message_text("⏹️ Stopped.", parse_mode="Markdown")

        elif action == "refresh":
            await query.edit_message_text("🔄 Refreshing...")
            filename = take_screenshot()
            if filename and os.path.exists(filename):
                with open(filename, 'rb') as f:
                    await query.message.reply_photo(photo=f, caption=f"📸 {datetime.now().strftime('%H:%M:%S')}")
                os.remove(filename)
            await query.edit_message_text("💻 *Monitor*", parse_mode="Markdown", reply_markup=get_monitor_keyboard())

async def handle_message(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages."""
    user_id = update.effective_user.id
    user_message = update.message.text

    if user_id not in user_states:
        user_states[user_id] = {'chat_enabled': True, 'selected_skill': None, 'prompt_mode': False, 'monitoring': False}

    state = user_states[user_id]

    # Analyze input
    lang = detect_language(user_message)
    role, task_type, tech_stack = analyze_task(user_message)

    if state.get('selected_skill'):
        role = state['selected_skill']

    prompt = build_prompt(role, task_type, tech_stack, lang, user_message)

    if state.get('prompt_mode'):
        tech_str = f" | 📦 {', '.join(tech_stack)}" if tech_stack else ""
        await update.message.reply_text(
            f"🎯 *Generated*\n👤 {role.capitalize()} | 📋 {task_type}{tech_str} | 🌐 {lang}",
            parse_mode="Markdown"
        )

    await update.message.reply_text("🤔 Processing...")

    try:
        response = await ai_team.arun(prompt)
        await update.message.reply_text(f"🤖 {response}")
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")

def main():
    """Start the bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not found in .env")
        print("Get token from @BotFather")
        return

    # Check for screenshot dependencies
    try:
        import mss
    except ImportError:
        print("📦 Installing mss for screenshots...")
        os.system("pip install mss pillow -q")

    try:
        import psutil
    except ImportError:
        print("📦 Installing psutil for system info...")
        os.system("pip install psutil -q")

    print("🚀 Starting Prompt Master Bot with Live Screen...")

    app = Application.builder().token(token).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("screen", screen_command))
    app.add_handler(CommandHandler("live", live_command))
    app.add_handler(CommandHandler("stop", stop_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("prompt", prompt_command))
    app.add_handler(CommandHandler("chat", chat_command))
    app.add_handler(CommandHandler("skill", skill_command))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot ready!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()