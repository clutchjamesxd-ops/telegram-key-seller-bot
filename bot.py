import random
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# ===== CONFIG =====
TOKEN = "8758244481:AAFvmUcNNrmMKDgp3hqX1osX58ApYomC3n0"
ADMIN_ID = 8271376829

# ===== DATABASE =====
users = {}
keys_stock = ["KEY-111", "KEY-222", "KEY-333"]

pending_funds = {}


# ===== MAIN MENU =====
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Buy Key", callback_data="buy")],
        [InlineKeyboardButton("💰 Add Fund", callback_data="addfund")],
        [InlineKeyboardButton("📜 History", callback_data="history")],
        [InlineKeyboardButton("💰 Balance", callback_data="balance")]
    ])


# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in users:
        users[user_id] = {"fund": 0, "history": []}

    await update.message.reply_text(
        "🌟 Premium Store Bot ❤️",
        reply_markup=main_menu()
    )


# ===== BUY KEY =====
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if users[user_id]["fund"] < 10:
        await query.message.reply_text("❌ Minimum fund required")
        return

    if not keys_stock:
        await query.message.reply_text("❌ Out of stock")
        return

    users[user_id]["fund"] -= 10

    key = random.choice(keys_stock)
    keys_stock.remove(key)

    users[user_id]["history"].append(
        f"Purchased Key | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )

    await query.message.reply_text(f"✅ Your Key:\n{key}")


# ===== ADD FUND MENU =====
async def addfund_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_photo(
        photo=open("qr.jpg", "rb"),
        caption=
        "❤️ Trusted Payment System\n\n"
        "💰 Minimum = 30\n"
        "💰 Maximum = 500\n\n"
        "👉 Type amount you want to add\n"
        "👉 Then send payment screenshot 📸"
    )


# ===== MESSAGE HANDLER =====
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # User sends amount
    if update.message.text and update.message.text.isdigit():

        amount = int(update.message.text)

        if amount < 30 or amount > 500:
            await update.message.reply_text("❌ Amount must be 30 - 500")
            return

        pending_funds[user_id] = amount

        await update.message.reply_text(
            "✅ Amount Accepted\nNow send payment screenshot 📸"
        )

        await context.bot.send_message(
            ADMIN_ID,
            f"💰 Fund Request\nUser: {user_id}\nAmount: {amount}"
        )

    # User sends screenshot
    if update.message.photo and user_id in pending_funds:

        photo = update.message.photo[-1].file_id
        amount = pending_funds[user_id]

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
            ]
        ])

        await context.bot.send_photo(
            ADMIN_ID,
            photo=photo,
            caption=f"💰 Fund Request\nUser: {user_id}\nAmount: {amount}",
            reply_markup=keyboard
        )

        await update.message.reply_text(
            "✅ Screenshot sent for verification ❤️"
        )


# ===== ADMIN APPROVAL =====
async def admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if update.effective_user.id != ADMIN_ID:
        return

    action, user_id = query.data.split("_")
    user_id = int(user_id)

    if user_id not in pending_funds:
        return

    amount = pending_funds[user_id]

    if action == "approve":

        users[user_id]["fund"] += amount

        await context.bot.send_message(
            user_id,
            f"✅ Payment Approved ❤️\nAmount Added: {amount}"
        )

        await query.message.reply_text("✅ Approved")

        try:
            await query.message.delete()
        except:
            pass

    else:

        await context.bot.send_message(
            user_id,
            "❌ Payment Rejected"
        )

        await query.message.reply_text("❌ Rejected")

    del pending_funds[user_id]


# ===== BUTTON HANDLER =====
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "buy":
        await buy(update, context)

    elif query.data == "addfund":
        await addfund_menu(update, context)

    elif query.data == "history":
        user_id = query.from_user.id
        hist = users.get(user_id, {}).get("history", [])
        await query.message.reply_text(
            "\n".join(hist) if hist else "No History"
        )

    elif query.data == "balance":
        user_id = query.from_user.id
        bal = users.get(user_id, {}).get("fund", 0)
        await query.message.reply_text(f"💰 Balance: {bal}")


# ===== MAIN =====
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(CallbackQueryHandler(admin_action))
app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))

print("Bot Running...")
app.run_polling()        pending_funds[user_id] = amount

        await update.message.reply_text(
            "✅ Amount Accepted\nNow send payment screenshot 📸"
        )

        await context.bot.send_message(
            ADMIN_ID,
            f"💰 Fund Request\nUser: {user_id}\nAmount: {amount}"
        )

    # User sends screenshot
    if update.message.photo and user_id in pending_funds:

        photo = update.message.photo[-1].file_id
        amount = pending_funds[user_id]

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
            ]
        ])

        await context.bot.send_photo(
            ADMIN_ID,
            photo=photo,
            caption=f"💰 Fund Request\nUser: {user_id}\nAmount: {amount}",
            reply_markup=keyboard
        )

        await update.message.reply_text(
            "✅ Screenshot sent for verification ❤️"
        )


# ================= ADMIN APPROVAL =================
async def admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if update.effective_user.id != ADMIN_ID:
        return

    action, user_id = query.data.split("_")
    user_id = int(user_id)

    if user_id not in pending_funds:
        return

    amount = pending_funds[user_id]

    if action == "approve":

        users[user_id]["fund"] += amount

        await context.bot.send_message(
            user_id,
            f"✅ Payment Approved ❤️\nAmount Added: {amount}"
        )

        await context.bot.send_message(
            ADMIN_ID,
            f"✅ Fund Added To User {user_id}\nAmount: {amount}"
        )

        try:
            await query.message.delete()
        except:
            pass

    else:

        await context.bot.send_message(
            user_id,
            "❌ Payment Rejected"
        )

        await query.message.reply_text("❌ Rejected")

    del pending_funds[user_id]


# ================= BUTTON HANDLER =================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "buy":
        await buy(update, context)

    elif query.data == "addfund":
        await addfund_menu(update, context)

    elif query.data == "history":
        user_id = query.from_user.id
        hist = users.get(user_id, {}).get("history", [])
        await query.message.reply_text(
            "\n".join(hist) if hist else "No History"
        )

    elif query.data == "balance":
        user_id = query.from_user.id
        bal = users.get(user_id, {}).get("fund", 0)
        await query.message.reply_text(f"💰 Balance: {bal}")


# ================= MAIN =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(CallbackQueryHandler(admin_action))
app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))

print("Bot Running...")
app.run_polling()            await update.message.reply_text("❌ Amount must be 30 - 500")
            return

        pending_funds[user_id] = amount

        await update.message.reply_text(
            "✅ Amount accepted\nNow send payment screenshot 📸"
        )

        await context.bot.send_message(
            ADMIN_ID,
            f"💰 Fund Request\nUser: {user_id}\nAmount: {amount}"
        )

    # User sends screenshot
    if update.message.photo and user_id in pending_funds:

        photo = update.message.photo[-1].file_id
        amount = pending_funds[user_id]

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
            ]
        ])

        await context.bot.send_photo(
            ADMIN_ID,
            photo=photo,
            caption=f"💰 Fund Request\nUser: {user_id}\nAmount: {amount}",
            reply_markup=keyboard
        )

        await update.message.reply_text(
            "✅ Screenshot sent for verification ❤️"
        )


# ================= ADMIN APPROVE / REJECT =================
async def admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if update.effective_user.id != ADMIN_ID:
        return

    action, user_id = query.data.split("_")
    user_id = int(user_id)

    if user_id not in pending_funds:
        return

    amount = pending_funds[user_id]

    if action == "approve":
        users[user_id]["fund"] += amount

        await context.bot.send_message(
            user_id,
            f"✅ Fund Added Successfully ❤️\nAmount: {amount}"
        )

        await query.message.reply_text("✅ Approved")

    else:
        await context.bot.send_message(
            user_id,
            "❌ Fund Request Rejected"
        )

        await query.message.reply_text("❌ Rejected")

    del pending_funds[user_id]


# ================= BUTTON HANDLER =================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "buy":
        await buy(update, context)

    elif query.data == "addfund":
        await addfund_menu(update, context)

    elif query.data == "history":
        user_id = query.from_user.id
        hist = users.get(user_id, {}).get("history", [])
        await query.message.reply_text(
            "\n".join(hist) if hist else "No History"
        )

    elif query.data == "balance":
        user_id = query.from_user.id
        bal = users.get(user_id, {}).get("fund", 0)
        await query.message.reply_text(f"💰 Balance: {bal}")


# ================= MAIN =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(CallbackQueryHandler(admin_action))
app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))

print("Bot Running...")
app.run_polling()
