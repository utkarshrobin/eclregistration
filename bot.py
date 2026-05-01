from flask import Flask
from threading import Thread

app_web = Flask('')

@app_web.route('/')
def home():
    return "Bot is running!"

def run_web():
    app_web.run(host='0.0.0.0', port=10000)

Thread(target=run_web).start()
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

# Required channels/groups
REQUIRED_GROUP_1 = "@eclplays"
REQUIRED_GROUP_2 = "@ecllogs"

# Log channel ID
LOG_CHANNEL = -1003708644771

# Store registered users
registered_users = set()


# =========================
# CHECK JOIN FUNCTION
# =========================

async def is_user_joined(bot, chat_username, user_id):
    try:
        member = await bot.get_chat_member(
            chat_username,
            user_id
        )

        return member.status in [
            "member",
            "administrator",
            "creator"
        ]

    except:
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
        "👋 Hi ! welcome to the ECL registration bot kindly join this two channel to continue and /start .",
        reply_markup=InlineKeyboardMarkup(keyboard)
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

    # Prevent duplicate registration
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

    # If user not joined
    if not joined_group or not joined_logs:

        await send_join_message(update.message)
        return

    # Show role buttons
    await show_role_buttons(update.message)


# =========================
# TRY AGAIN BUTTON
# =========================

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

print("🏏 ECL BOT RUNNING...")

app.run_polling()
