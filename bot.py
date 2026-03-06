import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# ===== CONFIG =====
TOKEN = "8758244481:AAFvmUcNNrmMKDgp3hqX1osX58ApYomC3n0"
ADMIN_ID = 8271376829

# ===== DATABASE =====
users = {}
keys_stock = ["KEY-111", "KEY-222", "KEY-333"]

fund_requests = {}   # user_id -> (amount, message_id)
earnings = 0


# ================= MAIN MENU =================
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Buy Key", callback_data="buy")],
        [InlineKeyboardButton("💰 Add Fund", callback_data="addfund")],
        [InlineKeyboardButton("🎁 My Keys", callback_data="mykeys")],
        [InlineKeyboardButton("💰 Balance", callback_data="balance")]
    ])


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in users:
        users[user_id] = {"fund": 0, "keys": [], "history": []}

    await update.message.reply_text(
        "🔥 Welcome To Digital Store",
        reply_markup=main_menu_keyboard()
    )


# ================= BUY KEY =================
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if users[user_id]["fund"] < 10:
        await query.message.reply_text("❌ Minimum fund = 10")
        return

    if not keys_stock:
        await query.message.reply_text("❌ Out of stock")
        return

    users[user_id]["fund"] -= 10

    key = random.choice(keys_stock)
    keys_stock.remove(key)

    users[user_id]["keys"].append(key)

    await query.message.reply_text(f"✅ Your Key:\n{key}")


# ================= ADD FUND MENU =================
async def addfund_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("50", callback_data="fund_50")],
        [InlineKeyboardButton("100", callback_data="fund_100")],
        [InlineKeyboardButton("200", callback_data="fund_200")],
        [InlineKeyboardButton("⬅ Back", callback_data="back")]
    ])

    await query.message.reply_text(
        "💰 Select Fund Amount",
        reply_markup=keyboard
    )


# ================= FUND REQUEST PROCESS =================
async def fund_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    amount = int(query.data.split("_")[1])
    user_id = query.from_user.id

    msg = await query.message.reply_text(
        f"Send payment screenshot for {amount} 💰"
    )

    fund_requests[user_id] = (amount, msg.message_id)

    await context.bot.send_message(
        ADMIN_ID,
        f"💰 Fund Request\nUser: {user_id}\nAmount: {amount}\n\n"
        "Reply with:\n/approve USERID\n/reject USERID"
    )


# ================= BUTTON HANDLER =================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "buy":
        await buy(update, context)

    elif data == "addfund":
        await addfund_menu(update, context)

    elif data.startswith("fund_"):
        await fund_amount(update, context)

    elif data == "mykeys":
        user_id = query.from_user.id
        keys = users.get(user_id, {}).get("keys", [])
        await query.message.reply_text("\n".join(keys) if keys else "No keys")

    elif data == "balance":
        user_id = query.from_user.id
        bal = users.get(user_id, {}).get("fund", 0)
        await query.message.reply_text(f"💰 Balance: {bal}")

    elif data == "back":
        await query.message.reply_text(
            "Main Menu",
            reply_markup=main_menu_keyboard()
        )


# ================= ADMIN APPROVE =================
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        return

    user_id = int(context.args[0])

    if user_id in fund_requests:
        amount, msg_id = fund_requests[user_id]

        users[user_id]["fund"] += amount

        del fund_requests[user_id]

        await context.bot.send_message(
            user_id,
            f"✅ Fund Added Successfully\nAmount: {amount}"
        )

        await update.message.reply_text("✅ Approved")

        # Notify admin
        await context.bot.send_message(
            ADMIN_ID,
            f"💰 Fund Added To User {user_id}"
        )


# ================= ADMIN REJECT =================
async def reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        return

    user_id = int(context.args[0])

    if user_id in fund_requests:
        del fund_requests[user_id]

        await context.bot.send_message(
            user_id,
            "❌ Fund Request Rejected"
        )

        await update.message.reply_text("Rejected")


# ================= MAIN =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("approve", approve))
app.add_handler(CommandHandler("reject", reject))

app.add_handler(CallbackQueryHandler(button_handler))

print("Bot Running...")
app.run_polling()        await update.message.reply_text("Use:\n/addkey KEY")


async def stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text("Stock:\n" + "\n".join(keys_stock))


async def earnings_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text(f"💵 Earnings: {earnings}")


# ================= MAIN =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("addkey", addkey))
app.add_handler(CommandHandler("stock", stock))
app.add_handler(CommandHandler("earnings", earnings_cmd))

app.add_handler(CallbackQueryHandler(button_handler))

print("Bot Running...")
app.run_polling()
