from pyrogram import Client, filters
from pyrogram.errors import RPCError
import asyncio

# =========================
# CONFIG
# =========================
API_ID = 31383535
API_HASH = "4d5fede55dedce694a86391c23b31eb5"
BOT_TOKEN = "8688993454:AAEZNTQ4-fb8irVzUCGFIyYESvDABkCxMOI"

USERS_FILE = "cleaned_registered_users.txt"

# =========================
# BOT START
# =========================
app = Client(
    "GiveSetsBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# =========================
# READ IDS
# =========================
def load_user_ids():
    ids = []

    with open(USERS_FILE, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if line.isdigit():
                ids.append(int(line))

    return ids


# =========================
# FORMAT USER DATA
# =========================
def format_user_data(user):
    data = []

    if user.first_name:
        data.append(f"First Name: {user.first_name}")

    if user.username:
        data.append(f"Username: @{user.username}")

    data.append(f"ID: {user.id}")

    return " | ".join(data)


# =========================
# /givesets COMMAND
# =========================
@app.on_message(filters.command("givesets"))
async def give_sets(client, message):

    await message.reply_text("Started fetching users...")

    user_ids = load_user_ids()

    valid_users = []
    no_data_users = []

    # =========================
    # FETCH USERS
    # =========================
    for uid in user_ids:

        try:
            user = await client.get_users(uid)

            valid_users.append(format_user_data(user))

        except RPCError:
            no_data_users.append(uid)

        except Exception:
            no_data_users.append(uid)

        await asyncio.sleep(0.2)

    # =========================
    # SEND VALID USER SETS
    # =========================
    set_number = 1

    for i in range(0, len(valid_users), 10):

        chunk = valid_users[i:i + 10]

        text = f"Set-{set_number}\n\n"

        for user_data in chunk:
            text += f"{user_data}\n\n"

        await message.reply_text(text)

        set_number += 1

    # =========================
    # SEND NO DATA SET
    # =========================
    if no_data_users:

        no_data_set = 1

        for i in range(0, len(no_data_users), 10):

            chunk = no_data_users[i:i + 10]

            text = f"No Data Set-{no_data_set}\n\n"

            for uid in chunk:
                text += f"ID: {uid}\n"

            await message.reply_text(text)

            no_data_set += 1

    await message.reply_text("Finished sending all sets.")


# =========================
# RUN BOT
# =========================
app.run()
