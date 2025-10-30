import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime, time
from bot_core import *

# Get DEVELOPMENT Environment
load_dotenv('.env.dev', override=True)

logger.info("Starting DEV bot...")

# # Timezone
TIMEZONE = ZoneInfo(os.getenv('TIMEZONE'))
print(f"Using TIMEZONE: {TIMEZONE}")

def get_current_day():
    """Returns the current day (1-24)"""
    now = datetime.now(TIMEZONE)
    # For october 1-31
    if now.month == 10 and 1 <= now.day <= 31:
        return now.day
    return None

# Bot Commands
async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display list of available riddles"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT day_number FROM riddles ORDER BY day_number;')
    days = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    
    if not days:
        await update.message.reply_text("❌ No riddle in the database!")
        return
    
    message = "📋 **Available riddle:**\n\n"
    for day in days:
        message += f"Tag {day}: /riddle{day}\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context, is_dev=True)

async def riddle_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await riddle(update, context, get_current_day, is_dev=True)

async def riddle_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await riddle_command(update, context, get_current_day, is_dev=True)

async def handle_riddle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_answer(update, context)

def main():
    """Start DEV bot"""
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not found in .env.dev!")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("riddle", riddle_today))
    application.add_handler(CommandHandler("list", list_command))
    
    # Dynamic handler for /riddle{day}
    for day in range(1, 32):
        application.add_handler(CommandHandler(f"riddle{day}", riddle_day))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_riddle_answer))
    
    logger.info("✅ DEV Bot started!")
    
    # Start Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()