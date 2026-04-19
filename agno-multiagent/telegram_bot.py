"""
Telegram Bot - AI Chat Interface
Send /start to begin
"""
import os
import logging
from dotenv import load_dotenv
load_dotenv()

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from agent_system import ai_team

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(
        "🤖 *SAI Rolotech AI Bot*\n\n"
        "I am your AI assistant powered by Agno + Gemini.\n\n"
        "Send me any question or task!",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await update.message.reply_text(
        "📚 *Commands:*\n\n"
        "/start - Start the bot\n"
        "/help - Show this help\n"
        "/agents - List available agents\n"
        "/chat - Chat with AI team",
        parse_mode="Markdown"
    )

async def agents_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /agents command"""
    await update.message.reply_text(
        "👥 *Available Agents:*\n\n"
        "1️⃣ *Researcher* - Research & information\n"
        "2️⃣ *Coder* - Code writing & review\n"
        "3️⃣ *Analyst* - Data analysis & insights",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages"""
    user_message = update.message.text

    await update.message.reply_text("🤔 Processing your request...")

    try:
        # Get AI response
        response = await ai_team.arun(user_message)
        await update.message.reply_text(f"🤖 {response}")
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")

def main():
    """Start the Telegram bot"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not found in .env")
        print("Get your token from @BotFather on Telegram")
        return

    print("🚀 Starting Telegram Bot...")

    app = Application.builder().token(token).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("agents", agents_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot ready! Press Ctrl+C to stop")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
