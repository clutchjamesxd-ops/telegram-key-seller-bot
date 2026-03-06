import random
from telegram import *
from telegram.ext import *

TOKEN = "8758244481:AAHy51oS3ZJSn5N-UMTQG0Od1TKRsuQDbrs"
ADMIN_ID = 8271376829

KEY_PRICE = 20

users = {}
keys_stock = []
pending_payments = {}
waiting_amount = {}
waiting_add_keys = {}
waiting_remove_key = {}
waiting_ss = {}
earnings = 0


# ---------------- MAIN MENU TEXT ----------------

def main_menu_text():

    return (
        "🔥 Welcome to Premium Key Store\n\n"
        "⚡ Fast delivery\n"
        "🔐 Secure payments\n"
        "💎 Premium service\n\n"
        "Choose an option below 👇"
    )


# ---------------- MAIN MENU BUTTONS ----------------

def main_menu():

    keyboard = [
        [InlineKeyboardButton("🛒 Buy Key", callback_data="buy")],
        [InlineKeyboardButton("💰 Add Fund", callback_data="addfund")],
        [InlineKeyboardButton("💳 Balance", callback_data="balance")],
        [InlineKeyboardButton("📜 History", callback_data="history")]
    ]

    return InlineKeyboardMarkup(keyboard)


# ---------------- ADMIN MENU ----------------

def admin_menu():

    keyboard = [
        [InlineKeyboardButton("➕ Add Keys", callback_data="admin_add")],
        [InlineKeyboardButton("➖ Remove Key", callback_data="admin_remove")],
        [InlineKeyboardButton("📦 Stock", callback_data="admin_stock")],
        [InlineKeyboardButton("👥 Users", callback_data="admin_users")],
        [InlineKeyboardButton("💰 Earnings", callback_data="admin_earn")],
        [InlineKeyboardButton("🔙 Back", callback_data="menu")]
    ]

    return InlineKeyboardMarkup(keyboard)


# ---------------- START ----------------

def start(update, context):

    user_id = update.effective_user.id

    if user_id not in users:
        users[user_id] = {"fund":0,"history":[]}

    update.message.reply_text(
        main_menu_text(),
        reply_markup=main_menu()
    )


# ---------------- BUTTON HANDLER ----------------

def buttons(update, context):

    global earnings

    query = update.callback_query
    query.answer()

    user_id = query.from_user.id
    data = query.data

    # BUY KEY
    if data == "buy":

        if users[user_id]["fund"] < KEY_PRICE:
            query.edit_message_text(
                f"❌ Insufficient balance\nKey Price = ₹{KEY_PRICE}",
                reply_markup=main_menu()
            )
            return

        if len(keys_stock) == 0:
            query.edit_message_text("❌ Out of stock", reply_markup=main_menu())
            return

        key = random.choice(keys_stock)
        keys_stock.remove(key)

        users[user_id]["fund"] -= KEY_PRICE
        users[user_id]["history"].append(key)

        earnings += KEY_PRICE

        query.edit_message_text(
            f"✅ Purchase Successful\n\n🔑 Your Key:\n`{key}`",
            parse_mode="Markdown",
            reply_markup=main_menu()
        )


    # BALANCE
    elif data == "balance":

        bal = users[user_id]["fund"]

        query.edit_message_text(
            f"💳 Your Balance: ₹{bal}",
            reply_markup=main_menu()
        )


    # HISTORY
    elif data == "history":

        hist = users[user_id]["history"]

        text = "\n".join(hist) if hist else "No purchases yet"

        query.edit_message_text(
            f"📜 Purchase History\n\n{text}",
            reply_markup=main_menu()
        )


    # ADD FUND
    elif data == "addfund":

        waiting_amount[user_id] = True

        query.edit_message_text(
            "💰 Add Funds\n\n"
            "Minimum ₹30\nMaximum ₹500\n\n"
            "Send the amount you want to add.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="menu")]
            ])
        )


    elif data == "menu":

        query.edit_message_text(
            main_menu_text(),
            reply_markup=main_menu()
        )


    # ADMIN PANEL
    elif data == "admin_add":

        waiting_add_keys[user_id] = True

        query.edit_message_text(
            "Send keys separated by new line\nExample:\nKEY1\nKEY2"
        )


    elif data == "admin_remove":

        waiting_remove_key[user_id] = True

        query.edit_message_text(
            "Send key to remove"
        )


    elif data == "admin_stock":

        query.edit_message_text(
            f"📦 Stock = {len(keys_stock)} keys",
            reply_markup=admin_menu()
        )


    elif data == "admin_users":

        query.edit_message_text(
            f"👥 Users = {len(users)}",
            reply_markup=admin_menu()
        )


    elif data == "admin_earn":

        query.edit_message_text(
            f"💰 Earnings = ₹{earnings}",
            reply_markup=admin_menu()
        )


# ---------------- TEXT HANDLER ----------------

def text_handler(update, context):

    user_id = update.effective_user.id
    text = update.message.text

    # ADD FUND AMOUNT
    if user_id in waiting_amount:

        try:
            amount = int(text)
        except:
            update.message.reply_text("Send valid number")
            return

        if amount < 30 or amount > 500:
            update.message.reply_text("Amount must be ₹30 - ₹500")
            return

        pending_payments[user_id] = amount
        waiting_ss[user_id] = True

        del waiting_amount[user_id]

        update.message.reply_photo(
            open("qr.jpg","rb"),
            caption=f"💰 Pay ₹{amount}\n\nThen send payment screenshot."
        )
        return


    # ADMIN ADD KEYS
    if user_id in waiting_add_keys:

        keys = text.split("\n")

        for k in keys:
            keys_stock.append(k)

        del waiting_add_keys[user_id]

        update.message.reply_text(
            f"✅ {len(keys)} keys added",
            reply_markup=admin_menu()
        )
        return


    # ADMIN REMOVE KEY
    if user_id in waiting_remove_key:

        if text in keys_stock:
            keys_stock.remove(text)
            msg = "Key removed"
        else:
            msg = "Key not found"

        del waiting_remove_key[user_id]

        update.message.reply_text(msg, reply_markup=admin_menu())
        return


# ---------------- SCREENSHOT ----------------

def screenshot(update, context):

    user_id = update.effective_user.id

    if user_id not in waiting_ss:
        return

    photo = update.message.photo[-1].file_id
    amount = pending_payments[user_id]

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
        ]
    ])

    context.bot.send_photo(
        ADMIN_ID,
        photo,
        caption=f"Payment Request\nUser: {user_id}\nAmount: ₹{amount}",
        reply_markup=keyboard
    )

    update.message.reply_text("Payment sent for approval")

    del waiting_ss[user_id]


# ---------------- APPROVAL ----------------

def approval(update, context):

    query = update.callback_query
    query.answer()

    data = query.data

    if data.startswith("approve_"):

        uid = int(data.split("_")[1])
        amount = pending_payments[uid]

        users[uid]["fund"] += amount

        context.bot.send_message(
            uid,
            f"✅ Payment Approved\n₹{amount} added to your balance"
        )

        query.edit_message_caption("✅ Approved")

        del pending_payments[uid]


    elif data.startswith("reject_"):

        uid = int(data.split("_")[1])

        context.bot.send_message(uid, "❌ Payment Rejected")

        query.edit_message_caption("❌ Rejected")

        del pending_payments[uid]


# ---------------- RUN BOT ----------------

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("admin", lambda u,c: u.message.reply_text("⚙ Admin Panel", reply_markup=admin_menu()) if u.effective_user.id==ADMIN_ID else None))

dp.add_handler(CallbackQueryHandler(buttons))
dp.add_handler(CallbackQueryHandler(approval, pattern="approve_|reject_"))

dp.add_handler(MessageHandler(Filters.text & ~Filters.command, text_handler))
dp.add_handler(MessageHandler(Filters.photo, screenshot))

print("Bot Started")
updater.start_polling()
updater.idle()
