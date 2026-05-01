import os
import json
import threading

from flask import Flask

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
# CONFIG
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")

REQUIRED_GROUP_1 = -1003752945686
REQUIRED_GROUP_2 = -1003708644771

LOG_CHANNEL = -1003708644771

USERS_FILE = "registered_users.json"

# =========================
# FLASK SERVER
# =========================

web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "ECL Bot Running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

# =========================
# LOAD USERS
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
    with open(USERS_FILE, "w") as file:
        json.dump(list(registered_users), file)

# =========================
# CHECK JOIN
# =========================

async def is_user_joined(bot, chat_id, user_id):

    try:
        member = await bot.get_chat_member(chat_id, user_id)

        return member.status not in ["left", "kicked"]

    except Exception as e:
        print(e)
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
        "👋 Hi! Welcome to the ECL registration bot.\n\n"
        "Kindly join these two channels/groups to continue.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================
# ROLE BUTTONS
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
# /START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    if user.id in registered_users:

        await update.message.reply_text(
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

    if not joined_group or not joined_logs:

        await send_join_message(update.message)
        return

    await show_role_buttons(update.message)

# =========================
# CHECK JOIN
# =========================

async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user = query.from_user

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

    if not joined_group or not joined_logs:

        await send_join_message(query.message)
        return

    await show_role_buttons(query.message)

# =========================
# ROLE SELECTED
# =========================

async def role_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user = query.from_user
    role = query.data

    if user.id in registered_users:

        await query.message.reply_text(
            "✅ You have already registered."
        )

        return

    registered_users.add(user.id)
    save_users()

    username = (
        f"@{user.username}"
        if user.username
        else "No Username"
    )

    log_message = f"""
🏏 NEW PLAYER ENTRY

👤 Name: {user.first_name}

📛 Username: {username}

🎯 Role: {role}

🆔 User ID: {user.id}
"""

    try:
        await context.bot.send_message(
            chat_id=LOG_CHANNEL,
            text=log_message
        )

    except Exception as e:
        print(e)

    await query.message.reply_text(
        "✅🏏 Registration successful!\n\n"
        "📢 Check your registration at @ecllogs"
    )

# =========================
# SHOW JSON
# =========================

async def show_json(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not os.path.exists(USERS_FILE):

        await update.message.reply_text(
            "❌ No registered users yet."
        )

        return

    await context.bot.send_document(
        chat_id=update.effective_chat.id,
        document=open(USERS_FILE, "rb")
    )

# =========================
# MAIN
# =========================

def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("showjson", show_json)
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

    print("🏏 ECL BOT RUNNING...")

    app.run_polling()

# =========================
# START BOTH
# =========================

threading.Thread(target=run_web).start()

main()
