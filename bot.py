import os
import json
import logging

from flask import Flask
from threading import Thread

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# =========================
# LOGGING
# =========================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# =========================
# FLASK KEEP ALIVE
# =========================

app_web = Flask(__name__)

@app_web.route("/")
def home():
    return "🏏 ECL Bot is running!"

def run_web():
    app_web.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        use_reloader=False
    )

Thread(target=run_web, daemon=True).start()

# =========================
# CONFIG
# =========================

BOT_TOKEN = "8688993454:AAEZNTQ4-fb8irVzUCGFIyYESvDABkCxMOI"

# Required channels/groups
REQUIRED_GROUP_1 = -1003752945686
REQUIRED_GROUP_2 = -1003708644771

# Log channel
LOG_CHANNEL = -1003708644771

# JSON database
USERS_FILE = "registered_users.json"

# =========================
# LOAD REGISTERED USERS
# =========================

try:

    with open(USERS_FILE, "r") as file:
        registered_users = set(json.load(file))

except:

    registered_users = set()

# =========================
# SAVE USERS
# =========================

def save_users():

    temp_file = USERS_FILE + ".tmp"

    with open(temp_file, "w") as file:
        json.dump(list(registered_users), file)

    os.replace(temp_file, USERS_FILE)

# =========================
# CHECK JOIN FUNCTION
# =========================

async def is_user_joined(bot, chat_id, user_id):

    try:

        member = await bot.get_chat_member(
            chat_id=chat_id,
            user_id=user_id
        )

        return member.status not in [
            "left",
            "kicked"
        ]

    except Exception as e:

        logging.error(
            f"Join check failed: {e}"
        )

        return False

# =========================
# JOIN MESSAGE
# =========================

async def send_join_message(message):

    keyboard = [

        [
            InlineKeyboardButton(
                "🏏 JOIN CRIC GC",
                url="https://t.me/eclplays"
            )
        ],

        [
            InlineKeyboardButton(
                "📢 JOIN LOG CHANNEL",
                url="https://t.me/ecllogs"
            )
        ],

        [
            InlineKeyboardButton(
                "✅ TRY AGAIN",
                callback_data="check_join"
            )
        ]
    ]

    await message.reply_text(
        "👋 Welcome to the ECL Registration Bot!\n\n"
        "📢 Kindly join both channels/groups below to continue.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================
# SHOW JSON
# =========================

async def show_json(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not os.path.exists(USERS_FILE):

        await update.message.reply_text(
            "❌ No registration file found."
        )

        return

    await context.bot.send_document(
        chat_id=update.effective_chat.id,
        document=open(USERS_FILE, "rb")
    )

# =========================
# SHOW ROLE BUTTONS
# =========================

async def show_role_buttons(message):

    keyboard = [

        [
            InlineKeyboardButton(
                "🎯 Bowler",
                callback_data="Bowler"
            )
        ],

        [
            InlineKeyboardButton(
                "🏏 Batter",
                callback_data="Batter"
            )
        ],

        [
            InlineKeyboardButton(
                "🔥 All Rounder",
                callback_data="All Rounder"
            )
        ]
    ]

    await message.reply_text(
        "🏏 Select your role 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================
# /START COMMAND
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    # Already registered
    if int(user.id) in registered_users:

        await update.message.reply_text(
            "✅ You are already registered in ECL."
        )

        return

    # Check memberships
    joined_group = await is_user_joined(
        context.bot,
        REQUIRED_GROUP_1,
        user.id
    )

    joined_logs = await is_user_joined(
        context.bot,
        REQUIRED_GROUP_2,
        user.id
    )

    # Not joined
    if not joined_group or not joined_logs:

        await send_join_message(
            update.message
        )

        return

    # Show roles
    await show_role_buttons(
        update.message
    )

# =========================
# TRY AGAIN BUTTON
# =========================

async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    # Remove old buttons
    try:
        await query.message.edit_reply_markup(
            reply_markup=None
        )
    except:
        pass

    user = query.from_user

    # Already registered
    if int(user.id) in registered_users:

        await query.message.reply_text(
            "✅ You are already registered in ECL."
        )

        return

    # Check memberships
    joined_group = await is_user_joined(
        context.bot,
        REQUIRED_GROUP_1,
        user.id
    )

    joined_logs = await is_user_joined(
        context.bot,
        REQUIRED_GROUP_2,
        user.id
    )

    # Not joined
    if not joined_group or not joined_logs:

        await send_join_message(
            query.message
        )

        return

    # Verified
    await show_role_buttons(
        query.message
    )

# =========================
# ROLE SELECTION
# =========================

async def role_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    # Remove buttons
    try:
        await query.message.edit_reply_markup(
            reply_markup=None
        )
    except:
        pass

    user = query.from_user
    role = query.data

    # Already registered
    if int(user.id) in registered_users:

        await query.message.reply_text(
            "✅ You are already registered."
        )

        return

    # Recheck membership
    joined_group = await is_user_joined(
        context.bot,
        REQUIRED_GROUP_1,
        user.id
    )

    joined_logs = await is_user_joined(
        context.bot,
        REQUIRED_GROUP_2,
        user.id
    )

    if not joined_group or not joined_logs:

        await query.message.reply_text(
            "❌ You must join required channels first."
        )

        return

    # Save user
    registered_users.add(
        int(user.id)
    )

    save_users()

    # Username handling
    username = (
        f"@{user.username}"
        if user.username
        else "No Username"
    )

    # Log message
    log_message = f"""
🏏 NEW PLAYER ENTRY

👤 Name: {user.first_name}

📛 Username: {username}

🎯 Role: {role}

🆔 User ID: {user.id}
"""

    # Send logs safely
    try:

        await context.bot.send_message(
            chat_id=LOG_CHANNEL,
            text=log_message
        )

    except Exception as e:

        logging.error(
            f"Log send failed: {e}"
        )

    # Success message
    await query.message.reply_text(
        "✅ Registration Successful!\n\n"
        "🏏 Welcome to ECL.\n"
        "📢 Check logs at @ecllogs"
    )

# =========================
# MAIN
# =========================

app = (
    ApplicationBuilder()
    .token(BOT_TOKEN)
    .build()
)

# Commands
app.add_handler(
    CommandHandler(
        "start",
        start
    )
)

app.add_handler(
    CommandHandler(
        "showjson",
        show_json
    )
)

# Buttons
app.add_handler(
    CallbackQueryHandler(
        check_join,
        pattern="check_join"
    )
)

app.add_handler(
    CallbackQueryHandler(
        role_selected,
        pattern="^(Bowler|Batter|All Rounder)$"
    )
)

print("🏏 ECL BOT RUNNING...")

# Run bot
app.run_polling(
    drop_pending_updates=True
    )=============

async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user = query.from_user

    # Prevent duplicate registration
    if user.id in registered_users:

        await query.message.reply_text(
            "✅ You have already registered in ECL."
        )

        return

    joined_group = await is_user_joined(
        context.bot,
        REQUIRED_GROUP_1,
        user.id
    )

    joined_logs = await is_user_joined(
        context.bot,
        REQUIRED_GROUP_2,
        user.id
    )

    # Still not joined
    if not joined_group or not joined_logs:

        await send_join_message(query.message)
        return

    # Verified
    await show_role_buttons(query.message)


# =========================
# ROLE SELECTION
# =========================

async def role_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user = query.from_user
    role = query.data

    # Prevent duplicate registration
    if user.id in registered_users:

        await query.message.reply_text(
            "✅ You have already registered."
        )

        return

    # Save registered user
    registered_users.add(user.id)
    save_users()

    username = (
        f"@{user.username}"
        if user.username
        else "@none"
    )

    log_message = f"""
🏏 NEW PLAYER ENTRY

👤 Name: {user.first_name}
📛 Username: {username}
🎯 Role: {role}
🆔 User ID: {user.id}
"""

    # Send to log channel
    await context.bot.send_message(
        chat_id=LOG_CHANNEL,
        text=log_message
    )

    await query.message.reply_text(
    "✅🏏 Registration successful!\n\n"
    "📢 Check your registration at @ecllogs"

    )


# =========================
# MAIN
# =========================

app = ApplicationBuilder().token(
    "8688993454:AAEZNTQ4-fb8irVzUCGFIyYESvDABkCxMOI"
).build()

app.add_handler(
    CommandHandler("start", start)
)

app.add_handler(
    CallbackQueryHandler(
        check_join,
        pattern="check_join"
    )
)

app.add_handler(
    CallbackQueryHandler(
        role_selected,
        pattern="^(Bowler|Batter|All Rounder)$"
    )
)
app.add_handler(CommandHandler("showjson", show_json))

print("🏏 ECL BOT RUNNING...")

app.run_polling()
