"""
Telegram Bot - Prompt Master (Standalone Version)
Simple Telegram bot with Prompt Builder + Live Screen
Run: python telegram_bot.py
"""
import os
import re
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# User states
user_states = {}

# Skills
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

# Role prompts
ROLES = {
    'educator': "You are an expert educator who explains concepts clearly.",
    'engineer': "You are a senior software engineer.",
    'debugger': "You are a debugging expert.",
    'reviewer': "You are a code reviewer.",
    'writer': "You are a content writer.",
    'devops': "You are a DevOps engineer.",
    'security': "You are a cybersecurity expert.",
    'data': "You are a data analyst.",
    'business': "You are a business strategist.",
    'support': "You are a technical support specialist.",
}

def take_screenshot():
    """Take screenshot."""
    try:
        import mss
        with mss.mss() as sct:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{ts}.png"
            sct.shot(output=filename)
            return filename
    except Exception as e:
        logger.error(f"Screenshot error: {e}")
        return None

def get_system_info():
    """Get system stats."""
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        return f"💻 *System Status*\n\n🔲 CPU: {cpu}%\n🧠 RAM: {mem.percent}%\n💾 Used: {mem.used // (1024**3)}GB / {mem.total // (1024**3)}GB"
    except:
        return "💻 System Info (psutil not available)"

def analyze_task(text):
    """Analyze input and detect domain."""
    lower = text.lower()
    # Debugging
    debug = ['bug', 'error', 'issue', 'problem', 'fail', 'kaam nahi', 'chal nahi', 'exception', 'crash']
    if any(p in lower for p in debug):
        return 'debugger', 'debugging'
    # Security
    sec = ['security', 'auth', 'password', 'jwt', 'oauth', 'vulnerability']
    if any(p in lower for p in sec):
        return 'security', 'security'
    # Review
    rev = ['review', 'analyze', 'audit', 'optimize', 'performance']
    if any(p in lower for p in rev):
        return 'reviewer', 'review'
    # Education
    edu = ['kaise', 'samjhao', 'explain', 'basics', 'kya hai', 'what is', 'tutorial']
    if any(p in lower for p in edu):
        return 'educator', 'education'
    # DevOps
    dev = ['ci/cd', 'docker', 'kubernetes', 'deploy', 'server', 'cloud', 'aws', 'database']
    if any(p in lower for p in dev):
        return 'devops', 'devops'
    # Content
    cont = ['blog', 'email', 'document', 'article', 'write']
    if any(p in lower for p in cont):
        return 'writer', 'content'
    return 'engineer', 'coding'

def detect_lang(text):
    """Detect Hindi/English."""
    return 'Hindi' if re.search(r'[\u0900-\u097F]', text) else 'English'

def build_prompt(role, task, lang, user_input):
    """Build structured prompt."""
    return f"""## Role
{ROLES.get(role, ROLES['engineer'])}

## Task Type
{task.capitalize()}

## Language
{lang}

## User Request
{user_input}

## Output
Provide clear, actionable response."""

def skill_keyboard():
    """Skill selection keyboard."""
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

def main_keyboard():
    """Main menu keyboard."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎯 Prompt Builder", callback_data="menu_prompt")],
        [InlineKeyboardButton("📸 Screenshot", callback_data="menu_screenshot")],
        [InlineKeyboardButton("💻 Live Monitor", callback_data="menu_monitor")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings")],
    ])

def monitor_keyboard():
    """Monitor controls."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📸 Snap", callback_data="monitor_snap")],
        [InlineKeyboardButton("▶️ Start 5s", callback_data="monitor_start_5")],
        [InlineKeyboardButton("⏹️ Stop", callback_data="monitor_stop")],
        [InlineKeyboardButton("🔄 Refresh", callback_data="monitor_refresh")],
    ])

async def start(update: Update, _context):
    """Start command."""
    uid = update.effective_user.id
    user_states[uid] = {'chat_enabled': True, 'selected_skill': None, 'prompt_mode': False, 'monitoring': False}
    await update.message.reply_text(
        "🤖 *SAI Rolotech AI Bot - Prompt Master*\n\n"
        "🎯 Features:\n"
        "• Prompt Builder\n"
        "• 📸 Screenshot\n"
        "• 💻 Live Monitor\n"
        "• 💻 System Info\n\n"
        "Type in Hindi/English!",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )

async def help_cmd(update: Update, _context):
    """Help command."""
    await update.message.reply_text(
        "📚 *Commands:*\n\n"
        "/start - Menu\n"
        "/screen - Screenshot\n"
        "/live - 5-frame stream\n"
        "/info - System info\n"
        "/prompt - Prompt Builder\n"
        "/stop - Stop monitor",
        parse_mode="Markdown"
    )

async def screen_cmd(update: Update, _context):
    """Take screenshot."""
    await update.message.reply_text("📸 Taking screenshot...")
    filename = take_screenshot()
    if filename and os.path.exists(filename):
        with open(filename, 'rb') as f:
            await update.message.reply_photo(photo=f, caption=f"📸 {datetime.now().strftime('%H:%M:%S')}")
        os.remove(filename)
    else:
        await update.message.reply_text("❌ Install mss: `pip install mss`")

async def live_cmd(update: Update, _context):
    """Live monitor."""
    uid = update.effective_user.id
    user_states[uid]['monitoring'] = True
    await update.message.reply_text("💻 *Live Monitor*\n\nTaking 5 frames...", parse_mode="Markdown")

    for i in range(5):
        if not user_states.get(uid, {}).get('monitoring', False):
            break
        filename = take_screenshot()
        if filename and os.path.exists(filename):
            with open(filename, 'rb') as f:
                await update.message.reply_photo(photo=f, caption=f"Frame {i+1}/5")
            os.remove(filename)
        await asyncio.sleep(1)

    user_states[uid]['monitoring'] = False
    await update.message.reply_text("✅ Live monitor complete!")

async def stop_cmd(update: Update, _context):
    """Stop monitor."""
    uid = update.effective_user.id
    if uid in user_states:
        user_states[uid]['monitoring'] = False
    await update.message.reply_text("⏹️ Monitoring stopped.")

async def info_cmd(update: Update, _context):
    """System info."""
    info = get_system_info()
    await update.message.reply_text(info, parse_mode="Markdown")

async def prompt_cmd(update: Update, _context):
    """Prompt builder."""
    uid = update.effective_user.id
    if uid not in user_states:
        user_states[uid] = {'chat_enabled': True, 'selected_skill': None, 'prompt_mode': True, 'monitoring': False}
    else:
        user_states[uid]['prompt_mode'] = True
    await update.message.reply_text("🎯 *Prompt Builder*\n\nSelect skill:", parse_mode="Markdown", reply_markup=skill_keyboard())

async def callback(update: Update, _context):
    """Handle callbacks."""
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    data = query.data

    if uid not in user_states:
        user_states[uid] = {'chat_enabled': True, 'selected_skill': None, 'prompt_mode': False, 'monitoring': False}

    # Skill selection
    if data.startswith("skill_"):
        skill = data.replace("skill_", "")
        if skill == "auto":
            user_states[uid]['selected_skill'] = None
            await query.edit_message_text("🔄 *Auto-Detect* enabled", parse_mode="Markdown")
        elif skill == "done":
            sel = user_states[uid].get('selected_skill')
            await query.edit_message_text(f"✅ Ready! Skill: {SKILLS.get(sel, 'Auto')}" if sel else "✅ Ready!", parse_mode="Markdown")
        else:
            user_states[uid]['selected_skill'] = skill
            await query.edit_message_text(f"✅ Skill: {SKILLS.get(skill, skill)}", parse_mode="Markdown", reply_markup=skill_keyboard())

    # Menu actions
    elif data.startswith("menu_"):
        menu = data.replace("menu_", "")
        if menu == "prompt":
            user_states[uid]['prompt_mode'] = True
            await query.edit_message_text("🎯 *Prompt Builder*", parse_mode="Markdown", reply_markup=skill_keyboard())
        elif menu == "screenshot":
            await query.edit_message_text("📸 Taking...")
            filename = take_screenshot()
            if filename and os.path.exists(filename):
                with open(filename, 'rb') as f:
                    await query.message.reply_photo(photo=f, caption=f"📸 {datetime.now().strftime('%H:%M:%S')}")
                os.remove(filename)
            await query.edit_message_text("💻 Menu", parse_mode="Markdown", reply_markup=main_keyboard())
        elif menu == "monitor":
            await query.edit_message_text("💻 *Live Monitor*", parse_mode="Markdown", reply_markup=monitor_keyboard())
        elif menu == "settings":
            state = user_states[uid]
            await query.edit_message_text(
                f"⚙️ *Settings*\n\n• Chat: {'🟢' if state.get('chat_enabled', True) else '🔴'}\n• Skill: {state.get('selected_skill', 'Auto')}",
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
            await query.edit_message_text("💻 Monitor", parse_mode="Markdown", reply_markup=monitor_keyboard())
        elif action == "start_5":
            user_states[uid]['monitoring'] = True
            await query.edit_message_text("💻 Taking 5 frames...")
            for i in range(5):
                if not user_states.get(uid, {}).get('monitoring', False):
                    break
                filename = take_screenshot()
                if filename and os.path.exists(filename):
                    with open(filename, 'rb') as f:
                        await query.message.reply_photo(photo=f, caption=f"Frame {i+1}/5")
                    os.remove(filename)
                await asyncio.sleep(1)
            user_states[uid]['monitoring'] = False
            await query.edit_message_text("✅ Done!", parse_mode="Markdown", reply_markup=monitor_keyboard())
        elif action == "stop":
            user_states[uid]['monitoring'] = False
            await query.edit_message_text("⏹️ Stopped.", parse_mode="Markdown")
        elif action == "refresh":
            await query.edit_message_text("🔄 Refreshing...")
            filename = take_screenshot()
            if filename and os.path.exists(filename):
                with open(filename, 'rb') as f:
                    await query.message.reply_photo(photo=f, caption=f"📸 {datetime.now().strftime('%H:%M:%S')}")
                os.remove(filename)
            await query.edit_message_text("💻 Monitor", parse_mode="Markdown", reply_markup=monitor_keyboard())

async def handle_message(update: Update, _context):
    """Handle messages."""
    uid = update.effective_user.id
    msg = update.message.text

    if uid not in user_states:
        user_states[uid] = {'chat_enabled': True, 'selected_skill': None, 'prompt_mode': False, 'monitoring': False}

    state = user_states[uid]
    lang = detect_lang(msg)
    role, task = analyze_task(msg)

    if state.get('selected_skill'):
        role = state['selected_skill']

    prompt = build_prompt(role, task, lang, msg)

    if state.get('prompt_mode'):
        await update.message.reply_text(
            f"🎯 *Generated*\n👤 {role.capitalize()} | 📋 {task} | 🌐 {lang}",
            parse_mode="Markdown"
        )

    await update.message.reply_text("🤔 Processing...")

    # Simple response (replace with your AI integration)
    response = f"""🤖 *Response*

**Skill:** {role.capitalize()}
**Task:** {task.capitalize()}
**Language:** {lang}

Your prompt has been structured! Add your AI API key to enable full AI responses.

*Install dependencies:* `pip install mss psutil python-telegram-bot`

Add your AI logic in handle_message() function."""

    await update.message.reply_text(response, parse_mode="Markdown")

def main():
    """Start bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        print("[ERROR] TELEGRAM_BOT_TOKEN not found in .env")
        print("[INFO] Get token from @BotFather")
        print("[INFO] Create .env file with: TELEGRAM_BOT_TOKEN=your_token_here")
        return

    # Auto-install dependencies
    try:
        import mss
    except:
        print("[INFO] Installing mss...")
        os.system("pip install mss -q")

    try:
        import psutil
    except:
        print("[INFO] Installing psutil...")
        os.system("pip install psutil -q")

    print("[OK] Starting Prompt Master Bot...")

    app = Application.builder().token(token).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("screen", screen_cmd))
    app.add_handler(CommandHandler("live", live_cmd))
    app.add_handler(CommandHandler("stop", stop_cmd))
    app.add_handler(CommandHandler("info", info_cmd))
    app.add_handler(CommandHandler("prompt", prompt_cmd))
    app.add_handler(CallbackQueryHandler(callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("[OK] Bot ready! Press Ctrl+C to stop")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()