import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ===== BOT TOKEN =====
TOKEN = "8758244481:AAFvmUcNNrmMKDgp3hqX1osX58ApYomC3n0"

# ===== ADMIN ID =====
ADMIN_ID = 8271376829   # Change to your Telegram ID

# ===== DATABASE (Simple Memory Version) =====
users = {}
keys_stock = ["KEY-111", "KEY-222", "KEY-333"]

earnings = 0

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in users:
        users[user_id] = {
            "fund": 0,
            "keys": [],
            "history": []
        }

    await update.message.reply_text(
        "🔥 Welcome to Key Seller Bot\n\n"
        "/buy - Buy Key\n"
        "/mykeys - My Keys\n"
        "/balance - Balance\n"
        "/history - Purchase History"
    )

# ================= BUY KEY =================
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global earnings

    user_id = update.effective_user.id

    if len(keys_stock) == 0:
        await update.message.reply_text("❌ Out of stock")
        return

    if users[user_id]["fund"] < 10:
        await update.message.reply_text("❌ Add fund first (Minimum 10)")
        return

    # Deduct money
    users[user_id]["fund"] -= 10
    earnings += 10

    key = random.choice(keys_stock)
    keys_stock.remove(key)

    users[user_id]["keys"].append(key)
    users[user_id]["history"].append(f"Bought Key {key}")

    await update.message.reply_text(f"✅ Purchased Key:\n{key}")

# ================= MY KEYS =================
async def mykeys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    keys = users.get(user_id, {}).get("keys", [])

    if not keys:
        await update.message.reply_text("You have no keys")
        return

    await update.message.reply_text("\n".join(keys))

# ================= BALANCE =================
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    bal = users.get(user_id, {}).get("fund", 0)
    await update.message.reply_text(f"💰 Balance: {bal}")

# ================= HISTORY =================
async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    hist = users.get(user_id, {}).get("history", [])

    if not hist:
        await update.message.reply_text("No history")
        return

    await update.message.reply_text("\n".join(hist))

# ================= ADMIN ADD KEY =================
async def addkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if context.args:
        key = context.args[0]
        keys_stock.append(key)
        await update.message.reply_text("✅ Key Added")
    else:
        await update.message.reply_text("Use:\n/addkey KEY")

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
