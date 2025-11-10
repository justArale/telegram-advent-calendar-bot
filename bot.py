import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime, time
from bot_core import *

# Get PRODUCTION Environment
load_dotenv('.env.prod', override=True)

logging.info("Starting prod bot...")

# Timezone
TIMEZONE = ZoneInfo(os.getenv('TIMEZONE'))
MONTH = int(os.getenv('MONTH'))
LAST_DAY = int(os.getenv('LAST_DAY'))

def get_current_day():
    """Returns the current day"""
    now = datetime.now(TIMEZONE)
    # Take month and end day from .env.prod
    if now.month == MONTH and 1 <= now.day <= LAST_DAY:
        return now.day
    return None

# Bot Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context, is_dev=False)

async def riddle_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await riddle(update, context, get_current_day, is_dev=False)

async def riddle_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await riddle_command(update, context, get_current_day, is_dev=False)

async def handle_riddle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_answer(update, context)

def main():
    """Start PROD bot"""
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not found in .env.prod!")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("riddle", riddle_today))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_riddle_answer))
    
    # Dynamic handler for /riddle{day}
    for day in range(1, LAST_DAY + 1):
        application.add_handler(CommandHandler(f"riddle{day}", riddle_day))
    
    logger.info("✅ Prod Bot started!")
    
    # Start Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)
if __name__ == '__main__':
    main()