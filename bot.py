import random
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext

TOKEN = "8758244481:AAHy51oS3ZJSn5N-UMTQG0Od1TKRsuQDbrs"
ADMIN_ID = 8271376829

KEY_PRICE = 20

users = {}
keys_stock = []
pending_payments = {}
waiting_amount = {}
waiting_ss = {}

waiting_add_keys = {}
waiting_remove_key = {}

earnings = 0

logging.basicConfig(level=logging.INFO)

# MAIN MENU
def main_menu():
    keyboard = [
        [InlineKeyboardButton("🛒 Buy Key", callback_data="buy")],
        [InlineKeyboardButton("💰 Add Fund", callback_data="addfund")],
        [InlineKeyboardButton("📜 Purchase History", callback_data="history")],
        [InlineKeyboardButton("💳 Balance", callback_data="balance")]
    ]
    return InlineKeyboardMarkup(keyboard)


# ADMIN MENU
def admin_menu():
    keyboard = [
        [InlineKeyboardButton("➕ Add Keys", callback_data="admin_add")],
        [InlineKeyboardButton("➖ Remove Key", callback_data="admin_remove")],
        [InlineKeyboardButton("📦 Check Stock", callback_data="admin_stock")],
        [InlineKeyboardButton("👥 Users", callback_data="admin_users")],
        [InlineKeyboardButton("💰 Earnings", callback_data="admin_earn")],
        [InlineKeyboardButton("🔙 Back", callback_data="menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


# START
def start(update: Update, context: CallbackContext):

    user_id = update.effective_user.id

    if user_id not in users:
        users[user_id] = {"fund": 0, "history": []}

    update.message.reply_text(
        "🔥 Welcome to Premium Key Store\n\n"
        "Buy premium access keys instantly.\n"
        "Fast delivery • Trusted service • Secure payment\n\n"
        "Use menu below.",
        reply_markup=main_menu()
    )


# ADMIN COMMAND
def admin(update: Update, context: CallbackContext):

    if update.effective_user.id != ADMIN_ID:
        return

    update.message.reply_text(
        "⚙ ADMIN PANEL",
        reply_markup=admin_menu()
    )


# BUTTON HANDLER
def buttons(update: Update, context: CallbackContext):

    global earnings

    query = update.callback_query
    query.answer()

    user_id = query.from_user.id
    data = query.data

    # BUY KEY
    if data == "buy":

        if len(keys_stock) == 0:
            query.edit_message_text("❌ Out of stock", reply_markup=main_menu())
            return

        if users[user_id]["fund"] < KEY_PRICE:
            query.edit_message_text(
                f"❌ Not enough balance\nKey price ₹{KEY_PRICE}",
                reply_markup=main_menu()
            )
            return

        key = random.choice(keys_stock)
        keys_stock.remove(key)

        users[user_id]["fund"] -= KEY_PRICE
        users[user_id]["history"].append(key)

        earnings += KEY_PRICE

        query.edit_message_text(
            f"✅ Key Purchased\n\n🔑 {key}",
            reply_markup=main_menu()
        )

    # BALANCE
    elif data == "balance":

        bal = users[user_id]["fund"]

        query.edit_message_text(
            f"💳 Balance: ₹{bal}",
            reply_markup=main_menu()
        )

    # HISTORY
    elif data == "history":

        hist = users[user_id]["history"]

        if not hist:
            text = "No purchases yet."
        else:
            text = "\n".join(hist)

        query.edit_message_text(
            f"📜 Purchase History\n\n{text}",
            reply_markup=main_menu()
        )

    # ADD FUND
    elif data == "addfund":

        waiting_amount[user_id] = True

        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="menu")]]

        query.edit_message_text(
            "💰 Add Fund\n\n"
            "Send amount you want to add.\n\n"
            "Minimum ₹30\nMaximum ₹500",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "menu":

        query.edit_message_text(
            "🏠 Main Menu",
            reply_markup=main_menu()
        )

    # ADMIN PANEL BUTTONS
    elif data == "admin_add":

        waiting_add_keys[user_id] = True

        query.edit_message_text(
            "Send keys separated by new line\n\nExample:\nKEY1\nKEY2\nKEY3",
            reply_markup=admin_menu()
        )

    elif data == "admin_remove":

        waiting_remove_key[user_id] = True

        query.edit_message_text(
            "Send key to remove",
            reply_markup=admin_menu()
        )

    elif data == "admin_stock":

        query.edit_message_text(
            f"📦 Stock: {len(keys_stock)} keys",
            reply_markup=admin_menu()
        )

    elif data == "admin_users":

        query.edit_message_text(
            f"👥 Total Users: {len(users)}",
            reply_markup=admin_menu()
        )

    elif data == "admin_earn":

        query.edit_message_text(
            f"💰 Earnings: ₹{earnings}",
            reply_markup=admin_menu()
        )

    elif data.startswith("approve_"):

        uid = int(data.split("_")[1])

        amount = pending_payments[uid]

        users[uid]["fund"] += amount

        context.bot.send_message(
            uid,
            f"✅ Payment Approved\n₹{amount} added to your balance"
        )

        query.edit_message_caption("✅ Payment Approved")

        del pending_payments[uid]

    elif data.startswith("reject_"):

        uid = int(data.split("_")[1])

        context.bot.send_message(
            uid,
            "❌ Payment Rejected"
        )

        query.edit_message_caption("❌ Payment Rejected")

        del pending_payments[uid]


# TEXT HANDLER
def text_handler(update: Update, context: CallbackContext):

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
            update.message.reply_text("Amount must be ₹30-₹500")
            return

        pending_payments[user_id] = amount
        waiting_ss[user_id] = True

        del waiting_amount[user_id]

        update.message.reply_photo(
            open("qr.jpg", "rb"),
            caption=f"Pay ₹{amount}\n\nSend screenshot after payment"
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

        update.message.reply_text(
            msg,
            reply_markup=admin_menu()
        )

        return


# SCREENSHOT HANDLER
def screenshot(update: Update, context: CallbackContext):

    user_id = update.effective_user.id

    if user_id not in waiting_ss:
        return

    photo = update.message.photo[-1].file_id
    amount = pending_payments[user_id]

    keyboard = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
        ]
    ]

    context.bot.send_photo(
        ADMIN_ID,
        photo,
        caption=f"Payment Request\nUser: {user_id}\nAmount: ₹{amount}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    update.message.reply_text("Payment sent for approval")

    del waiting_ss[user_id]


# RUN BOT
updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("admin", admin))

dp.add_handler(CallbackQueryHandler(buttons))

dp.add_handler(MessageHandler(Filters.text & ~Filters.command, text_handler))
dp.add_handler(MessageHandler(Filters.photo, screenshot))

print("Bot Started")

updater.start_polling()
updater.idle()
