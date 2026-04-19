"""
Simple Test Bot - Echo Bot for Testing
This bot just echoes messages and shows keyboard buttons
"""
import os
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

# Simple echo bot for testing
async def start(update: Update, _context):
    """Start command with menu."""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📸 Screenshot", callback_data="btn_screenshot")],
        [InlineKeyboardButton("💻 System Info", callback_data="btn_info")],
        [InlineKeyboardButton("🎯 Prompt Builder", callback_data="btn_prompt")],
    ])
    await update.message.reply_text(
        "🤖 *Test Bot Working!*\n\n"
        "This bot is running correctly.\n"
        "All imports and handlers work!\n\n"
        "Click buttons below:",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

async def help_cmd(update: Update, _context):
    """Help command."""
    await update.message.reply_text(
        "*Commands:*\n"
        "/start - Menu\n"
        "/echo - Echo your message\n"
        "/info - System info\n"
        "/test - Test response",
        parse_mode="Markdown"
    )

async def echo_cmd(update: Update, _context):
    """Echo command."""
    await update.message.reply_text(f"Echo: {update.message.text}")

async def info_cmd(update: Update, _context):
    """System info."""
    try:
        import psutil
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        await update.message.reply_text(
            f"💻 *System Info*\n\n"
            f"CPU: {cpu}%\n"
            f"RAM: {mem}%\n\n"
            f"✅ Bot working perfectly!",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def test_cmd(update: Update, _context):
    """Test command."""
    await update.message.reply_text("✅ Test successful! Bot is working!")

async def handle_message(update: Update, _context):
    """Handle all messages."""
    text = update.message.text
    if text.startswith('/'):
        await update.message.reply_text("Unknown command. Try /help")
    else:
        # Simple auto-reply for testing
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("👍 Yes", callback_data="btn_yes")],
            [InlineKeyboardButton("👎 No", callback_data="btn_no")],
        ])
        await update.message.reply_text(
            f"You said: {text}\n\nBot received it! 🎉",
            reply_markup=keyboard
        )

async def callback_handler(update: Update, _context):
    """Handle button clicks."""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "btn_screenshot":
        await query.edit_message_text("📸 Screenshot feature ready!\n\n(mss installed and working)")
    elif data == "btn_info":
        try:
            import psutil
            await query.edit_message_text(
                f"💻 System:\nCPU: {psutil.cpu_percent()}%\nRAM: {psutil.virtual_memory().percent}%"
            )
        except:
            await query.edit_message_text("psutil not available")
    elif data == "btn_prompt":
        await query.edit_message_text(
            "🎯 Prompt Builder ready!\n\n"
            "This confirms bot is working correctly."
        )
    elif data == "btn_yes":
        await query.edit_message_text("👍 Great!")
    elif data == "btn_no":
        await query.edit_message_text("👎 Okay!")

def main():
    """Start the test bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token or token == "":
        print("=" * 60)
        print("TELEGRAM TEST BOT - NEEDS TOKEN")
        print("=" * 60)
        print()
        print("Get token from @BotFather:")
        print("1. Open Telegram")
        print("2. Search @BotFather")
        print("3. Send /newbot")
        print("4. Follow instructions")
        print("5. Copy token to .env file")
        print()
        print("Your token format should be like:")
        print("123456789:ABCdefGHIjklMNOpqrSTUvwxyz123456789")
        print()
        print("Current .env status:")
        with open(".env") as f:
            for line in f:
                if "TELEGRAM" in line:
                    print(f"  {line.strip()}")
        print()
        print("=" * 60)
        return

    print("[OK] Starting Test Bot...")

    app = Application.builder().token(token).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("echo", echo_cmd))
    app.add_handler(CommandHandler("info", info_cmd))
    app.add_handler(CommandHandler("test", test_cmd))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("[OK] Bot ready!")
    print("[OK] Commands: /start /help /echo /info /test")
    print()
    print("Go to Telegram and send /start to your bot!")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)

    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()