import random
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = "PASTE_YOUR_TOKEN_HERE"
ADMIN_ID = 8271376829

users = {}
keys_stock = ["KEY-111", "KEY-222", "KEY-333"]
pending_funds = {}

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Buy Key", callback_data="buy")],
        [InlineKeyboardButton("💰 Add Fund", callback_data="addfund")],
        [InlineKeyboardButton("📜 History", callback_data="history")],
        [InlineKeyboardButton("💰 Balance", callback_data="balance")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in users:
        users[user_id] = {"fund": 0, "history": []}

    await update.message.reply_text(
        "🌟 Premium Digital Store ❤️",
        reply_markup=main_menu()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    # BUY KEY
    if data == "buy":

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
            f"Key Bought | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )

        await query.message.reply_text(f"✅ Your Key:\n{key}")

    # ADD FUND
    elif data == "addfund":

        await query.message.reply_photo(
            photo=open("qr.jpg", "rb"),
            caption="❤️ Trusted Payment\n\n"
                    "Minimum: 30\n"
                    "Maximum: 500\n\n"
                    "Send amount then send screenshot 📸"
        )

    # HISTORY
    elif data == "history":

        hist = users.get(user_id, {}).get("history", [])

        await query.message.reply_text(
            "\n".join(hist) if hist else "No purchase history"
        )

    # BALANCE
    elif data == "balance":

        bal = users.get(user_id, {}).get("fund", 0)
        await query.message.reply_text(f"💰 Balance: {bal}")

    # APPROVE PAYMENT
    elif data.startswith("approve_"):

        if user_id != ADMIN_ID:
            return

        uid = int(data.split("_")[1])

        if uid not in pending_funds:
            await query.message.reply_text("Request expired")
            return

        amount = pending_funds[uid]

        users.setdefault(uid, {"fund":0,"history":[]})
        users[uid]["fund"] += amount

        await context.bot.send_message(
            uid,
            f"✅ Payment Approved\n💰 Amount Added: {amount}"
        )

        await context.bot.send_message(
            ADMIN_ID,
            f"✅ Fund added to user {uid}"
        )

        del pending_funds[uid]

        await query.message.delete()

    # REJECT PAYMENT
    elif data.startswith("reject_"):

        if user_id != ADMIN_ID:
            return

        uid = int(data.split("_")[1])

        if uid not in pending_funds:
            return

        await context.bot.send_message(uid, "❌ Payment Rejected")

        del pending_funds[uid]

        await query.message.delete()

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.from_user.id

    # USER SEND AMOUNT
    if update.message.text and update.message.text.isdigit():

        amount = int(update.message.text)

        if amount < 30 or amount > 500:
            await update.message.reply_text("Amount must be between 30 - 500")
            return

        pending_funds[user_id] = amount

        await update.message.reply_text("Amount received. Now send screenshot 📸")

        await context.bot.send_message(
            ADMIN_ID,
            f"💰 Fund Request\nUser: {user_id}\nAmount: {amount}"
        )

    # USER SEND SCREENSHOT
    elif update.message.photo and user_id in pending_funds:

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
            caption=f"Payment Screenshot\nUser: {user_id}\nAmount: {amount}",
            reply_markup=keyboard
        )

        await update.message.reply_text("Screenshot sent to admin ❤️")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))

print("Bot Running...")
app.run_polling()
