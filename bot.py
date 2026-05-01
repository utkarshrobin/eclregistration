import os
import json

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

BOT_TOKEN = "8688993454:AAEZNTQ4-fb8irVzUCGFIyYESvDABkCxMOI"

# REQUIRED CHANNEL/GROUP IDS
# Replace REQUIRED_GROUP_1 with your real @eclplays ID
REQUIRED_GROUP_1 = -1001234567890

# ECL LOGS CHANNEL ID
REQUIRED_GROUP_2 = -1003708644771

# LOG CHANNEL
LOG_CHANNEL = -1003708644771

# JSON FILE
USERS_FILE = "registered_users.json"

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
        member = await bot.get_chat_member(
            chat_id,
            user_id
        )

        return member.status not in [
            "left",
            "kicked"
        ]

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

    # Already registered
    if user.id in registered_users:

        await update.message.reply_text(
            "✅ You have already registered in ECL."
        )

        return

    # Check joins
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

        await send_join_message(update.message)
        return

    # Show role selection
    await show_role_buttons(update.message)

# =========================
# TRY AGAIN
# =========================

async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user = query.from_user

    # Already registered
    if user.id in registered_users:

        await query.message.reply_text(
            "✅ You have already registered in ECL."
        )

        return

    # Check joins
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
# ROLE SELECTED
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

    # Save user
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

    # Send log
    await context.bot.send_message(
        chat_id=LOG_CHANNEL,
        text=log_message
    )

    # Success message
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

app = ApplicationBuilder().token(
    BOT_TOKEN
).build()

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