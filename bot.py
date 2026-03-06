import json
import random
from telegram import *
from telegram.ext import *

TOKEN = "8758244481:AAHy51oS3ZJSn5N-UMTQG0Od1TKRsuQDbrs"
ADMIN_ID = 8271376829

KEY_PRICE = 20

# ---------------- STORAGE ----------------

def load_json(file, default):
    try:
        with open(file,"r") as f:
            return json.load(f)
    except:
        return default

def save_json(file,data):
    with open(file,"w") as f:
        json.dump(data,f,indent=4)

keys_stock = load_json("keys.json",[])
users = load_json("users.json",{})
pending_payments = load_json("pending.json",{})

waiting_amount = {}
waiting_ss = {}

earnings = 0

# ---------------- UI ----------------

def main_text():
    return """
🔥 Premium Cc Store Bot

⚡ Instant Delivery
🔐 Secure Payment
💎 Trusted Seller

Choose option below 👇
"""

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Buy Key",callback_data="buy")],
        [InlineKeyboardButton("💰 Add Fund",callback_data="addfund")],
        [InlineKeyboardButton("💳 Balance",callback_data="balance")],
        [InlineKeyboardButton("📜 History",callback_data="history")]
    ])

def admin_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Keys",callback_data="admin_add")],
        [InlineKeyboardButton("➖ Remove Keys",callback_data="admin_remove")],
        [InlineKeyboardButton("📦 Stock",callback_data="admin_stock")],
        [InlineKeyboardButton("👥 Users",callback_data="admin_users")],
        [InlineKeyboardButton("💰 Earnings",callback_data="admin_earn")],
        [InlineKeyboardButton("🔙 Back",callback_data="menu")]
    ])

# ---------------- START ----------------

def start(update,context):

    uid = update.effective_user.id

    if uid not in users:
        users[uid]={"fund":0,"history":[]}

    save_json("users.json",users)

    update.message.reply_text(
        main_text(),
        reply_markup=main_menu()
    )

# ---------------- ADMIN ----------------

def admin(update,context):

    if update.effective_user.id != ADMIN_ID:
        return

    update.message.reply_text(
        "⚙ ADMIN PANEL",
        reply_markup=admin_menu()
    )

# ---------------- BUTTONS ----------------

def buttons(update,context):

    global earnings

    query = update.callback_query
    query.answer()

    uid = query.from_user.id
    data = query.data

    # USER BUY
    if data=="buy":

        if users[uid]["fund"] < KEY_PRICE:
            query.edit_message_text("❌ Low balance",reply_markup=main_menu())
            return

        if not keys_stock:
            query.edit_message_text("❌ Out of stock",reply_markup=main_menu())
            return

        key = random.choice(keys_stock)
        keys_stock.remove(key)

        users[uid]["fund"] -= KEY_PRICE
        users[uid]["history"].append(key)

        earnings += KEY_PRICE

        save_json("keys.json",keys_stock)
        save_json("users.json",users)

        query.edit_message_text(
            f"✅ Purchase Successful\n\n🔑 {key}",
            reply_markup=main_menu()
        )

    elif data=="balance":
        query.edit_message_text(
            f"💳 Balance: ₹{users[uid]['fund']}",
            reply_markup=main_menu()
        )

    elif data=="history":

        hist = users[uid]["history"]
        text = "\n".join(hist) if hist else "No history"

        query.edit_message_text(text,reply_markup=main_menu())

    elif data=="addfund":

        waiting_amount[uid]=True

        query.edit_message_text(
            "💰 Add Fund\nMin ₹30 | Max ₹500\nSend amount:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back",callback_data="menu")]
            ])
        )

    elif data=="menu":
        query.edit_message_text(main_text(),reply_markup=main_menu())

    # ADMIN PANEL
    if uid==ADMIN_ID:

        if data=="admin_add":
            query.edit_message_text("Send keys line by line")

        elif data=="admin_remove":
            query.edit_message_text("Send key to remove")

        elif data=="admin_stock":
            query.edit_message_text(f"📦 Stock = {len(keys_stock)}")

        elif data=="admin_users":
            query.edit_message_text(f"👥 Users = {len(users)}")

        elif data=="admin_earn":
            query.edit_message_text(f"💰 Earnings = ₹{earnings}",
                                    reply_markup=admin_menu())

# ---------------- TEXT HANDLER ----------------

def text_handler(update,context):

    uid = update.effective_user.id
    text = update.message.text

    # PAYMENT FLOW
    if uid in waiting_amount:

        try:
            amount=int(text)
        except:
            update.message.reply_text("Send valid amount")
            return

        if amount<30 or amount>500:
            update.message.reply_text("Amount must be ₹30-₹500")
            return

        pending_payments[uid]=amount
        waiting_ss[uid]=True

        save_json("pending.json",pending_payments)

        del waiting_amount[uid]

        update.message.reply_photo(
            open("qr.jpg","rb"),
            caption=f"""
💰 Payment Gateway

Amount: ₹{amount}

Scan QR and pay
Then send screenshot
"""
        )

        return

    # ADMIN ADD KEYS
    if uid==ADMIN_ID and "\n" in text:

        for k in text.split("\n"):
            keys_stock.append(k)

        save_json("keys.json",keys_stock)

        update.message.reply_text(
            "✅ Keys Added",
            reply_markup=admin_menu()
        )

# ---------------- SCREENSHOT ----------------

def screenshot(update,context):

    uid = update.effective_user.id

    if uid not in waiting_ss:
        return

    photo = update.message.photo[-1].file_id
    amount = pending_payments[uid]

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Approve",callback_data=f"approve_{uid}"),
            InlineKeyboardButton("❌ Reject",callback_data=f"reject_{uid}")
        ]
    ])

    context.bot.send_photo(
        ADMIN_ID,
        photo,
        caption=f"""
Payment Request

User: {uid}
Amount: ₹{amount}
""",
        reply_markup=keyboard
    )

    update.message.reply_text("Payment sent for approval")

    del waiting_ss[uid]

# ---------------- APPROVAL ----------------

def approval(update,context):

    query = update.callback_query
    query.answer()

    data = query.data

    if data.startswith("approve_"):

        uid=int(data.split("_")[1])

        amount=pending_payments[uid]

        users[uid]["fund"]+=amount

        save_json("users.json",users)

        context.bot.send_message(
            uid,
            f"✅ Payment Approved\n₹{amount} added"
        )

        query.edit_message_caption("✅ Approved")

        pending_payments.pop(uid,None)
        save_json("pending.json",pending_payments)

    elif data.startswith("reject_"):

        uid=int(data.split("_")[1])

        context.bot.send_message(uid,"❌ Payment Rejected")

        query.edit_message_caption("❌ Rejected")

        pending_payments.pop(uid,None)
        save_json("pending.json",pending_payments)

# ---------------- RUN ----------------

updater = Updater(TOKEN,use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start",start))
dp.add_handler(CommandHandler("admin",admin))

dp.add_handler(CallbackQueryHandler(buttons))
dp.add_handler(CallbackQueryHandler(approval,pattern="approve_|reject_"))

dp.add_handler(MessageHandler(Filters.text & ~Filters.command,text_handler))
dp.add_handler(MessageHandler(Filters.photo,screenshot))

print("Bot Started")
updater.start_polling()
updater.idle()
    # USER BUY
    if data=="buy":

        if users[uid]["fund"] < KEY_PRICE:
            query.edit_message_text("❌ Low balance",reply_markup=main_menu())
            return

        if not keys_stock:
            query.edit_message_text("❌ Out of stock",reply_markup=main_menu())
            return

        key = random.choice(keys_stock)
        keys_stock.remove(key)

        users[uid]["fund"] -= KEY_PRICE
        users[uid]["history"].append(key)

        earnings += KEY_PRICE

        save_json("keys.json",keys_stock)
        save_json("users.json",users)

        query.edit_message_text(
            f"✅ Purchase Successful\n\n🔑 {key}",
            reply_markup=main_menu()
        )

    elif data=="balance":
        query.edit_message_text(
            f"💳 Balance: ₹{users[uid]['fund']}",
            reply_markup=main_menu()
        )

    elif data=="history":

        hist = users[uid]["history"]
        text = "\n".join(hist) if hist else "No history"

        query.edit_message_text(text,reply_markup=main_menu())

    elif data=="addfund":

        waiting_amount[uid]=True

        query.edit_message_text(
            "💰 Add Fund\n\nMin ₹30 | Max ₹500\nSend amount:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back",callback_data="menu")]
            ])
        )

    elif data=="menu":
        query.edit_message_text(main_text(),reply_markup=main_menu())

    # ADMIN PANEL BUTTONS
    if uid==ADMIN_ID:

        if data=="admin_add":
            query.edit_message_text("Send keys line by line")

        elif data=="admin_remove":
            query.edit_message_text("Send key to remove")

        elif data=="admin_stock":
            query.edit_message_text(f"📦 Stock = {len(keys_stock)}")

        elif data=="admin_users":
            query.edit_message_text(f"👥 Users = {len(users)}")

        elif data=="admin_earn":
            query.edit_message_text(f"💰 Earnings = ₹{earnings}",
                                    reply_markup=admin_menu())

# ---------------- TEXT HANDLER ----------------

def text_handler(update,context):

    uid = update.effective_user.id
    text = update.message.text

    # ADD FUND
    if uid in waiting_amount:

        try:
            amount=int(text)
        except:
            update.message.reply_text("Send valid number")
            return

        if amount<30 or amount>500:
            update.message.reply_text("Amount must be ₹30-₹500")
            return

        pending_payments[uid]=amount
        waiting_ss[uid]=True

        save_json("pending.json",pending_payments)

        del waiting_amount[uid]

        update.message.reply_photo(
            open("qr.jpg","rb"),
            caption=f"💰 Pay ₹{amount}\nSend screenshot after payment"
        )

        return

    # ADMIN ADD KEYS
    if uid==ADMIN_ID and "\n" in text:

        for k in text.split("\n"):
            keys_stock.append(k)

        save_json("keys.json",keys_stock)

        update.message.reply_text(
            "✅ Keys added",
            reply_markup=admin_menu()
        )

# ---------------- SCREENSHOT ----------------

def screenshot(update,context):

    uid = update.effective_user.id

    if uid not in waiting_ss:
        return

    photo = update.message.photo[-1].file_id
    amount = pending_payments[uid]

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Approve",callback_data=f"approve_{uid}"),
            InlineKeyboardButton("❌ Reject",callback_data=f"reject_{uid}")
        ]
    ])

    context.bot.send_photo(
        ADMIN_ID,
        photo,
        caption=f"Payment Request\nUser: {uid}\nAmount: ₹{amount}",
        reply_markup=keyboard
    )

    update.message.reply_text("Payment sent for approval")

    del waiting_ss[uid]

# ---------------- APPROVAL ----------------

def approval(update,context):

    query = update.callback_query
    query.answer()

    data = query.data

    if data.startswith("approve_"):

        uid=int(data.split("_")[1])

        amount=pending_payments[uid]

        users[uid]["fund"]+=amount

        save_json("users.json",users)

        context.bot.send_message(
            uid,
            f"✅ Payment Approved\n₹{amount} added"
        )

        query.edit_message_caption("✅ Approved")

        pending_payments.pop(uid,None)
        save_json("pending.json",pending_payments)

    elif data.startswith("reject_"):

        uid=int(data.split("_")[1])

        context.bot.send_message(uid,"❌ Payment Rejected")

        query.edit_message_caption("❌ Rejected")

        pending_payments.pop(uid,None)
        save_json("pending.json",pending_payments)

# ---------------- RUN ----------------

updater = Updater(TOKEN,use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start",start))
dp.add_handler(CommandHandler("admin",admin))

dp.add_handler(CallbackQueryHandler(buttons))
dp.add_handler(CallbackQueryHandler(approval,pattern="approve_|reject_"))

dp.add_handler(MessageHandler(Filters.text & ~Filters.command,text_handler))
dp.add_handler(MessageHandler(Filters.photo,screenshot))

print("Bot Started")
updater.start_polling()
updater.idle()
