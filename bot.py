import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# ===== BOT TOKEN =====
TOKEN = "PASTE_YOUR_TOKEN_HERE"

# ===== ADMIN ID =====
ADMIN_ID = 8271376829

# ===== DATABASE =====
users = {}
keys_stock = ["KEY-111", "KEY-222", "KEY-333"]

earnings = 0


# ================= START MENU =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in users:
        users[user_id] = {
            "fund": 0,
            "keys": [],
            "history": []
        }

    keyboard = [
        [InlineKeyboardButton("🛒 Buy Key", callback_data="buy")],
        [InlineKeyboardButton("🎁 My Keys", callback_data="mykeys")],
        [InlineKeyboardButton("💰 Balance", callback_data="balance")],
        [InlineKeyboardButton("📜 History", callback_data="history")]
    ]

    await update.message.reply_text(
        "🔥 Welcome to Digital Key Store\nChoose option below 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ================= BUY KEY =================
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global earnings

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if user_id not in users:
        return

    if len(keys_stock) == 0:
        await query.message.reply_text("❌ Out of stock")
        return

    if users[user_id]["fund"] < 10:
        await query.message.reply_text("❌ Minimum fund required = 10")
        return

    users[user_id]["fund"] -= 10
    earnings += 10

    key = random.choice(keys_stock)
    keys_stock.remove(key)

    users[user_id]["keys"].append(key)
    users[user_id]["history"].append(f"Bought {key}")

    await query.message.reply_text(f"✅ Purchased Key:\n{key}")


# ================= BUTTON HANDLER =================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    data = query.data

    if data == "buy":
        await buy(update, context)

    elif data == "mykeys":
        keys = users.get(user_id, {}).get("keys", [])
        await query.message.reply_text("\n".join(keys) if keys else "No keys")

    elif data == "balance":
        bal = users.get(user_id, {}).get("fund", 0)
        await query.message.reply_text(f"💰 Balance: {bal}")

    elif data == "history":
        hist = users.get(user_id, {}).get("history", [])
        await query.message.reply_text("\n".join(hist) if hist else "No history")


# ================= ADMIN ADD KEY =================
async def addkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if context.args:
        keys_stock.append(context.args[0])
        await update.message.reply_text("✅ Key Added")
    else:
        await update.message.reply_text("Use:\n/addkey KEY")


# ================= STOCK =================
async def stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text(
        "Stock Keys:\n" + "\n".join(keys_stock)
    )


# ================= EARNINGS =================
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
app.run_polling()        await update.message.reply_text("Use:\n/addkey KEY")

# ================= ADMIN CHECK STOCK =================
async def stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text(
        "Stock Keys:\n" + "\n".join(keys_stock)
    )

# ================= ADMIN VIEW EARNINGS =================
async def earnings_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text(f"💵 Total Earnings: {earnings}")

# ================= MAIN =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("buy", buy))
app.add_handler(CommandHandler("mykeys", mykeys))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(CommandHandler("history", history))
app.add_handler(CommandHandler("addkey", addkey))
app.add_handler(CommandHandler("stock", stock))
app.add_handler(CommandHandler("earnings", earnings_cmd))

print("Bot Running...")
app.run_polling()
