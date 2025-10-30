import os
import psycopg2
from telegram import Update
from telegram.ext import ContextTypes
import logging
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_db_connection():
    return psycopg2.connect(os.getenv('DATABASE_URL'))

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

# Shared Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE, is_dev=False):
    """Start message"""
    if is_dev:
        text = (
            "🧪 **DEV advent calendar-Bot**\n\n"
            "Commands:\n"
            "/start - Show this message\n"
            "/riddle - Riddle of the day\n"
            "/riddle1 - /riddle24 - Display riddle for day X\n"
            "/list - Display all available riddle\n\n"
            "Send your answer as text message!"
        )
    else:
        text = (
            "🎄 *Advent Riddle Bot v1.0* 🎄✨\n\n"
            "Daily riddles await — some plain text, some in code.\n"
            "Solve them, claim your emoji loot. 🎁\n\n"
            "Commands:\n"
            "/start - Show this message\n"
            "/riddle - Today's challenge\n"
            "/riddle{1-24} - Pick an specific past riddle\n\n"
        )
    await update.message.reply_text(text, parse_mode='Markdown')

async def riddle(update: Update, context: ContextTypes.DEFAULT_TYPE, get_current_day_func, is_dev):
    """Send riddle of the day"""
    current_day = get_current_day_func()
    
    if is_dev:
        logger.info(f"Current day: {current_day}")
    
    if current_day is None:
        await update.message.reply_text(
            "🎄✨ The riddle advents calendar runs from December first until Christmas Eve!"
        )
        return
    
    riddle_data = get_riddle_for_day(current_day)
    
    if is_dev:
        logger.info(f"Riddle data: {riddle_data}")
    
    if riddle_data is None:
        await update.message.reply_text(f"❌ There is no riddle for the {current_day}. day.")
        return
    
    riddle_id, riddle_text = riddle_data
    
    context.user_data['current_riddle_id'] = riddle_id
    context.user_data['current_day'] = current_day
    
    await update.message.reply_text(
        f"🎁 **Riddle day {current_day}:**\n\n{riddle_text}",
        parse_mode='Markdown'
    )

async def riddle_command(update: Update, context: ContextTypes.DEFAULT_TYPE, get_current_day_func, is_dev=False):
    """Generic handler for /riddle{day}"""
    command = update.message.text.split()[0].replace('/', '')
    
    try:
        day = int(command.replace('riddle', ''))
    except ValueError:
        await update.message.reply_text("❌ Invalid command! Use /riddle1 - /riddle24")
        return
    
    if is_dev:
        logger.info(f"Requested riddle for day: {day}")
    
    current_day = get_current_day_func()
    
    if current_day is None:
        await update.message.reply_text(
            "🎅 Ho ho... not so fast, clever coder! 🎄\n\n"
            "The Advent Calendar only runs from *December 1st to Christmas Eve!* 🎁"
        )
        return

    if day > current_day:
        await update.message.reply_text(
            "❌ Whoa there, time traveler! ❄️\n\n"
            "You can't peek at *future riddles* — Santa hasn't wrapped them yet! 🎁"
        )
        return

    if not 1 <= day <= 31:
        await update.message.reply_text(
            "❌ Oops! That day doesn't exist in Santa's schedule!\n\n"
            "Please choose a day *between 1 and 24!* 🎁"
        )
        return
    
    riddle_data = get_riddle_for_day(day)
    
    if is_dev:
        logger.info(f"Riddle data: {riddle_data}")
    
    if riddle_data is None:
        await update.message.reply_text(f"❌ No riddle for day {day}.")
        return
    
    riddle_id, riddle_text = riddle_data
    
    context.user_data['current_riddle_id'] = riddle_id
    context.user_data['current_day'] = day
    
    await update.message.reply_text(
        f"🎁 **Riddle day {day}:**\n\n{riddle_text}",
        parse_mode='Markdown'
    )

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
        await update.message.reply_text(f"🎉 *Right!* Day {day}")
        # And day is not the 24th
        if day != 24:
            await update.message.reply_text("You can open: " + result[0])
        # Day is the 24th
        if day == 24:
            await update.message.reply_text(result[0])
        
        # Delete current riddle from user data
        context.user_data['current_riddle_id'] = None
        context.user_data['current_day'] = None
    else:
        await update.message.reply_text("❌ Wrong, Again!")