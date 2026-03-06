import random
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ===== CONFIG =====
TOKEN = "8758244481:AAFvmUcNNrmMKDgp3hqX1osX58ApYomC3n0"
ADMIN_ID = 8271376829

# ===== DATABASE =====
users = {}
keys_stock = ["KEY-111", "KEY-222", "KEY-333"]

pending_funds = {}   # user_id -> amount
earnings = 0


# ================= MAIN MENU =================
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Buy Key", callback_data="buy")],
        [InlineKeyboardButton("💰 Add Fund", callback_data="addfund")],
        [InlineKeyboardButton("📜 History", callback_data="history")],
        [InlineKeyboardButton("💰 Balance", callback_data="balance")]
    ])


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in users:
        users[user_id] = {"fund": 0, "history": []}

    await update.message.reply_text(
        "🔥 Welcome Seller Store",
        reply_markup=main_menu()
    )


# ================= BUY =================
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
        f"Bought Key {key} | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )

    await query.message.reply_text(f"✅ Your Key:\n{key}")


# ================= ADD FUND =================
async def addfund(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    try:
        amount = int(context.args[0])

        if amount < 30 or amount > 500:
            await update.message.reply_text(
                "❌ Amount must be between 30 and 500"
            )
            return

        pending_funds[user_id] = amount

        # Send QR + Payment Info
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅ Back", callback_data="back")]
        ])

        await update.message.reply_photo(
            photo=open("qr.jpg", "rb"),
            caption=f"💰 Pay {amount} and send payment screenshot\n\n"
                    "Then send screenshot here."
                    "\nWaiting for admin approval...",
            reply_markup=keyboard
        )

        # Notify Admin
        await context.bot.send_message(
            ADMIN_ID,
            f"💰 Fund Request\nUser: {user_id}\nAmount: {amount}\n"
            "Send screenshot to approve."
        )

    except:
        await update.message.reply_text("Use:\n/addfund AMOUNT")


# ================= SCREENSHOT HANDLER =================
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in pending_funds:
        return

    amount = pending_funds[user_id]

    photo = update.message.photo[-1].file_id

    # Forward to admin with approval buttons
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

    await update.message.reply_text("✅ Screenshot sent for approval")


# ================= ADMIN APPROVE / REJECT =================
async def admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if update.effective_user.id != ADMIN_ID:
        return

    data = query.data
    action, user_id = data.split("_")
    user_id = int(user_id)

    if user_id not in pending_funds:
        return

    amount = pending_funds[user_id]

    if action == "approve":
        users[user_id]["fund"] += amount

        await context.bot.send_message(
            user_id,
            f"✅ Fund Added Successfully\nAmount: {amount}"
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
        await query.message.reply_text(
            "💰 Type:\n/addfund AMOUNT\n\nMinimum 30 | Maximum 500"
        )

    elif query.data == "history":
        user_id = query.from_user.id
        hist = users.get(user_id, {}).get("history", [])
        await query.message.reply_text(
            "\n".join(hist) if hist else "No history"
        )

    elif query.data == "balance":
        user_id = query.from_user.id
        bal = users.get(user_id, {}).get("fund", 0)
        await query.message.reply_text(f"💰 Balance: {bal}")

    elif query.data == "back":
        await query.message.reply_text("Main Menu", reply_markup=main_menu())


# ================= MAIN =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("addfund", addfund))

app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(CallbackQueryHandler(admin_action))

app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

print("Bot Running...")
app.run_polling()
