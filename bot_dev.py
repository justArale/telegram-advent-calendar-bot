import os
import psycopg2
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
from zoneinfo import ZoneInfo
from datetime import datetime, time

# Get DEVELOPMENT Environment
load_dotenv('.env.dev', override=True)

# Timezone
TIMEZONE = ZoneInfo(os.getenv('TIMEZONE'))
print(f"Using TIMEZONE: {TIMEZONE}")

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
logger.info("Starting DEV bot...")

def get_db_connection():
    return psycopg2.connect(os.getenv('DATABASE_URL'))

def get_current_day():
    """Returns the current day (1-24)"""
    now = datetime.now(TIMEZONE)
    # For october 1-31
    if now.month == 10 and 1 <= now.day <= 31:
        return now.day
    return None

def get_riddle_for_day(day_number):
    """Get the riddle of a specific day"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, riddle_text FROM riddles WHERE day_number = %s;', (day_number,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result

def check_answer(riddle_id, user_answer):
    """Checking the answer (with JSONB)"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Search in JSONB Array (case-insensitive)
    cur.execute('''
        SELECT s.solution_content
        FROM answers a
        JOIN solutions s ON s.riddle_id = a.riddle_id
        WHERE a.riddle_id = %s 
        AND EXISTS (
            SELECT 1 FROM jsonb_array_elements_text(a.answer_text) AS elem
            WHERE LOWER(elem) = LOWER(%s)
        );
    ''', (riddle_id, user_answer.strip()))
    
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result

# Bot Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    await update.message.reply_text(
        "🧪 **DEV advent calendar-Bot**\n\n"
        "Commands:\n"
        "/riddle - Riddle of the day\n"
        "/riddle1 - /riddle24 - Display riddle for day X\n"
        "/list - Display all available riddle\n\n"
        "Send your answer as text message!",
        parse_mode='Markdown'
    )

async def riddle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send riddle of the day"""
    current_day = get_current_day()
    print(f"day: " + str(current_day))
    
    if current_day is None:
        await update.message.reply_text("🎅 The riddle advents calendar runs from December first until Christmas Eve!")
        return
    
    riddle_data = get_riddle_for_day(current_day)
    print(f"riddle_data: " + str(riddle_data))
    
    if riddle_data is None:
        await update.message.reply_text(f"❌ There is no riddle for the {current_day}. day.")
        return
    
    riddle_id, riddle_text = riddle_data
    
    # Save current riddle in user data
    context.user_data['current_riddle_id'] = riddle_id
    context.user_data['current_day'] = current_day
    
    await update.message.reply_text(
        f"🎁 **Riddle day {current_day}:**\n\n{riddle_text}",
        parse_mode='Markdown'
    )


async def riddle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generic handler for /riddle{day}"""
    # Extract commant (z.B. /riddle1 -> 1)
    command = update.message.text.split()[0].replace('/', '')
    
    # Remove "riddle" prefix
    try:
        day = int(command.replace('riddle', ''))
    except ValueError:
        await update.message.reply_text("❌ Invalid command! Use /riddle1 - /riddle24")
        return
    
    print(f"Requested riddle for day: {day}")
    
    current_day = get_current_day()
    if current_day is None:
        await update.message.reply_text("❌ 🎅 The riddle advents calendar runs from December first until Christmas Eve!")
        return

    if day > current_day:
        await update.message.reply_text("❌ You can't access future riddles!")
        return

    if not 1 <= day <= 24:
        await update.message.reply_text("❌ Day has to be between 1 - 24!")
        return
    
    riddle_data = get_riddle_for_day(day)
    print(f"day: " + str(riddle_data))
    
    if riddle_data is None:
        await update.message.reply_text(f"❌ No riddle for day {day}.")
        return
    
    riddle_id, riddle_text = riddle_data

    # Save current riddle in user data
    context.user_data['current_riddle_id'] = riddle_id
    context.user_data['current_day'] = day
    
    await update.message.reply_text(
        f"🎁 **Riddle day {day}:**\n\n{riddle_text}",
        parse_mode='Markdown'
    )

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

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user answers"""
    # Get current riddle
    riddle_id = context.user_data.get('current_riddle_id')
    day = context.user_data.get('current_day')
    
    user_answer = update.message.text

    # If no riddle is active, send different message
    if riddle_id is None:
        await update.message.reply_text(
            "🎁 Hmm... looks like Santa took the riddles for a test drive! 🛷💨\n\n"
            "Try /riddle to get today’s challenge or /riddle1–/riddle24 to pick a past one!"
        )
        return
    
    # Check answer
    result = check_answer(riddle_id, user_answer)
    
    if result:
        # If right answer
        await update.message.reply_text(f"🎉 **Right!** Day {day}")
        await update.message.reply_text("You can open: " + result[0])
        
        # Delete current riddle from user data
        context.user_data['current_riddle_id'] = None
        context.user_data['current_day'] = None
    else:
        await update.message.reply_text("❌ Wrong, Again!")


def main():
    """Start bot"""
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not found in .env.dev!")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("riddle", riddle))
    application.add_handler(CommandHandler("list", list_command))
    
    # Dynamic handler for /riddle{day}
    for day in range(1, 32):
        application.add_handler(CommandHandler(f"riddle{day}", riddle_command))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))
    
    logger.info("✅ DEV Bot started!")
    
    # Start Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()