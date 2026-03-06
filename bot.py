import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = "8758244481:AAFvmUcNNrmMKDgp3hqX1osX58ApYomC3n0"
ADMIN_ID = 8271376829

users = {}
keys_stock = []
pending_funds = {}
adding_keys = set()

KEY_PRICE = 10


# ================= MAIN MENU =================
def main_menu():
    keyboard = [
        [InlineKeyboardButton("🛒 Buy Key", callback_data="buy")],
        [InlineKeyboardButton("💰 Balance", callback_data="balance")],
        [InlineKeyboardButton("➕ Add Fund", callback_data="addfund")],
        [InlineKeyboardButton("📜 Purchase History", callback_data="history")]
    ]
    return InlineKeyboardMarkup(keyboard)


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_id not in users:
        users[user_id] = {
            "fund": 0,
            "history": []
        }

    await update.message.reply_text(
        "🔥 *Welcome to Premium Key Store*\n\n"
        "Buy game keys, tools and premium access.\n"
        "Fast delivery ⚡ Trusted service 🔐\n\n"
        "Select option below 👇",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )


# ================= MENU BUTTON HANDLER =================
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "buy":

        if len(keys_stock) == 0:
            await query.edit_message_text(
                "❌ Out of stock",
                reply_markup=main_menu()
            )
            return

        if users[user_id]["fund"] < KEY_PRICE:
            await query.edit_message_text(
                "❌ Not enough balance",
                reply_markup=main_menu()
            )
            return

        key = keys_stock.pop(0)

        users[user_id]["fund"] -= KEY_PRICE
        users[user_id]["history"].append(key)

        await query.edit_message_text(
            f"✅ *Purchase Successful*\n\n"
            f"🔑 Your Key:\n`{key}`",
            parse_mode="Markdown",
            reply_markup=main_menu()
        )

    elif query.data == "balance":

        bal = users[user_id]["fund"]

        await query.edit_message_text(
            f"💰 Your Balance: ₹{bal}",
            reply_markup=main_menu()
        )

    elif query.data == "history":

        hist = users[user_id]["history"]

        if not hist:
            text = "No purchases yet"
        else:
            text = "\n".join(hist)

        await query.edit_message_text(
            f"📜 Purchase History\n\n{text}",
            reply_markup=main_menu()
        )

    elif query.data == "addfund":

        await query.edit_message_text(
            "💰 *Add Funds*\n\n"
            "Send the amount you want to add.\n"
            "Minimum: ₹30\n"
            "Maximum: ₹500",
            parse_mode="Markdown"
        )

        pending_funds[user_id] = "waiting_amount"


# ================= AMOUNT MESSAGE =================
async def amount_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in pending_funds:
        return

    if pending_funds[user_id] != "waiting_amount":
        return

    try:
        amount = int(text)
    except:
        return

    if amount < 30 or amount > 500:
        await update.message.reply_text("Amount must be between 30 and 500")
        return

    pending_funds[user_id] = amount

    await update.message.reply_photo(
        photo=open("qr.jpg", "rb"),
        caption=f"Pay ₹{amount}\n\nSend payment screenshot after payment."
    )


# ================= SCREENSHOT =================
async def screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_id not in pending_funds:
        return

    amount = pending_funds[user_id]

    if amount == "waiting_amount":
        return

    photo = update.message.photo[-1].file_id

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
        ]
    ])

    msg = await context.bot.send_photo(
        ADMIN_ID,
        photo=photo,
        caption=f"Payment Request\n\nUser: {user_id}\nAmount: ₹{amount}",
        reply_markup=keyboard
    )

    pending_funds[user_id] = (amount, msg.message_id)

    await update.message.reply_text("Payment sent for approval.")


# ================= ADMIN APPROVAL =================
async def approval(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    data = query.data
    action, user_id = data.split("_")

    user_id = int(user_id)

    if user_id not in pending_funds:
        return

    amount, msg_id = pending_funds[user_id]

    if action == "approve":

        users[user_id]["fund"] += amount

        await context.bot.send_message(
            user_id,
            f"✅ Fund Added ₹{amount}"
        )

        await context.bot.send_message(
            ADMIN_ID,
            f"💰 Payment Approved\nUser {user_id}\nAmount ₹{amount}"
        )

    else:

        await context.bot.send_message(
            user_id,
            "❌ Payment Rejected"
        )

    await context.bot.delete_message(ADMIN_ID, msg_id)

    del pending_funds[user_id]


# ================= ADMIN PANEL =================
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    keyboard = [
        [InlineKeyboardButton("➕ Add Keys", callback_data="add_keys")],
        [InlineKeyboardButton("📦 Stock", callback_data="stock")],
        [InlineKeyboardButton("❌ Remove Key", callback_data="remove_key")]
    ]

    await update.message.reply_text(
        "🔧 Admin Panel",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ================= ADMIN MENU =================
async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    if query.data == "add_keys":

        adding_keys.add(ADMIN_ID)

        await query.edit_message_text(
            "Send keys separated by new lines\n\nExample:\nKEY-111\nKEY-222"
        )

    elif query.data == "stock":

        if not keys_stock:
            text = "No keys in stock"
        else:
            text = "\n".join(keys_stock)

        await query.edit_message_text(f"📦 Stock:\n{text}")

    elif query.data == "remove_key":

        if not keys_stock:
            await query.edit_message_text("No keys to remove")
            return

        key = keys_stock.pop()

        await query.edit_message_text(f"Removed key:\n{key}")


# ================= RECEIVE KEYS =================
async def receive_keys(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_id not in adding_keys:
        return

    keys = update.message.text.split("\n")

    count = 0

    for k in keys:
        k = k.strip()
        if k:
            keys_stock.append(k)
            count += 1

    adding_keys.remove(user_id)

    await update.message.reply_text(
        f"{count} keys added.\nTotal stock: {len(keys_stock)}"
    )


# ================= MAIN =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("admin", admin))

app.add_handler(CallbackQueryHandler(menu_handler, pattern="^(buy|balance|addfund|history)$"))
app.add_handler(CallbackQueryHandler(admin_menu, pattern="^(add_keys|stock|remove_key)$"))
app.add_handler(CallbackQueryHandler(approval, pattern="^(approve_|reject_)"))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, amount_message))
app.add_handler(MessageHandler(filters.PHOTO, screenshot))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_keys))

print("Bot Running...")
app.run_polling()
