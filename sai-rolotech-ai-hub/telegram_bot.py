"""
SAI Rolotech AI Hub - Telegram Bot
Connects OpenClaw to Hermes Router
"""

from dotenv import load_dotenv
load_dotenv()

import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from apps.hermes_agent.core.master_router import MasterRouter
from shared.utils.logging import log

# Get bot token from env
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Initialize router
router = MasterRouter()

# API base URL
API_BASE = os.getenv("HERMES_API_URL", "http://localhost:8505")


# ==================== HANDLERS ====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text("""
🤖 SAI Rolotech AI Hub

Welcome! I can help with:

📋 CRM: /lead add [name] [mobile]
📊 Stats: /stats
🌐 Desktop: /open [app]
⏰ Remind: /remind [message]
📋 Tasks: /task [description]
💬 Chat: Just type naturally!

Type /help for all commands.
""")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await update.message.reply_text("""
📚 SAI Rolotech AI Hub - Commands

**CRM:**
/lead add [Name] [Mobile] - Add new lead
/lead list - View all leads
/stats - Business statistics

**Desktop:**
/open [app] - Open application
/run [command] - Run command

**Automation:**
/remind [message] - Set reminder
/task [description] - Create task
/schedule [task] - Schedule automation

**General:**
/report - Daily business report
/help - Show this help

💬 Or just chat naturally!
""")


async def lead_add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add new lead"""
    try:
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("❌ Usage: /lead add [Name] [Mobile]")
            return

        name = args[0]
        mobile = args[1]

        # Call CRM API
        response = requests.post(
            f"{API_BASE}/crm/lead",
            json={"name": name, "mobile": mobile, "source": "telegram"}
        )

        if response.status_code == 200:
            await update.message.reply_text(f"""
✅ Lead Created!

📋 Name: {name}
📱 Mobile: {mobile}
📍 Source: Telegram
""")
        else:
            await update.message.reply_text("❌ Failed to create lead")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def lead_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all leads"""
    try:
        response = requests.get(f"{API_BASE}/crm/leads")

        if response.status_code == 200:
            data = response.json()
            leads = data.get("leads", [])

            if not leads:
                await update.message.reply_text("📋 No leads found!")
                return

            msg = "📋 Your Leads:\n\n"
            for lead in leads[:10]:  # Show first 10
                msg += f"• {lead['name']} - {lead['mobile']} [{lead['stage']}]\n"

            if len(leads) > 10:
                msg += f"\n...and {len(leads) - 10} more"

            await update.message.reply_text(msg)
        else:
            await update.message.reply_text("❌ Failed to fetch leads")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show business stats"""
    try:
        response = requests.get(f"{API_BASE}/crm/stats")

        if response.status_code == 200:
            data = response.json()
            await update.message.reply_text(f"""
📊 Business Statistics

Total Leads: {data.get('total_leads', 0)}

Stage Breakdown:
• New: {data.get('new', 0)}
• Contacted: {data.get('contacted', 0)}
• Won: {data.get('won', 0)}
""")
        else:
            await update.message.reply_text("❌ Failed to fetch stats")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def open_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Open an application"""
    try:
        if not context.args:
            await update.message.reply_text("❌ Usage: /open [app name]")
            return

        app = " ".join(context.args)

        await update.message.reply_text(f"🌐 Opening {app}...")

        # Process through Hermes
        result = router.process(
            user_id=update.effective_user.id,
            message=f"open {app}"
        )

        if result.get("response"):
            await update.message.reply_text(result["response"])

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def remind_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set a reminder"""
    try:
        if not context.args:
            await update.message.reply_text("❌ Usage: /remind [message]")
            return

        message = " ".join(context.args)

        await update.message.reply_text(f"🔔 Reminder set: {message}")

        # Process through Hermes
        result = router.process(
            user_id=update.effective_user.id,
            message=f"remind me {message}"
        )

        if result.get("response"):
            await update.message.reply_text(result["response"])

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create a task"""
    try:
        if not context.args:
            await update.message.reply_text("❌ Usage: /task [description]")
            return

        task = " ".join(context.args)

        await update.message.reply_text(f"📋 Task created: {task}")

        # Process through Hermes
        result = router.process(
            user_id=update.effective_user.id,
            message=f"create task {task}"
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle natural language chat"""
    try:
        message = update.message.text
        user_id = update.effective_user.id

        await update.message.reply_text("🤔 Thinking...")

        # Process through Hermes router
        result = router.process(user_id=user_id, message=message)

        response = result.get("response", "I couldn't process that.")

        await update.message.reply_text(response)

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    log.error(f"Telegram error: {context.error}")


# ==================== MAIN ====================

def main():
    """Start the bot"""
    if not BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not set in .env")
        print("Get your token from @BotFather on Telegram")
        return

    print("🤖 Starting SAI Rolotech Telegram Bot...")

    # Create application
    app = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("lead", lead_add_command))
    app.add_handler(CommandHandler("leads", lead_list_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("open", open_command))
    app.add_handler(CommandHandler("remind", remind_command))
    app.add_handler(CommandHandler("task", task_command))

    # Message handler (must be last)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))

    # Error handler
    app.add_error_handler(error_handler)

    print("✅ Bot ready! Press Ctrl+C to stop")
    print(f"🌐 API: {API_BASE}")

    # Start polling
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
