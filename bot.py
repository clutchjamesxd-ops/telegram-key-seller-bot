import os
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = "8758244481:AAGgx1ZmC7blLY2Ll7Hu6N66G9HsR4LlE3Y"

# ---- Database Simulation (Simple Version) ----
users = {}
keys_stock = ["KEY1-ABC", "KEY2-XYZ", "KEY3-123"]

# ---- Start Command ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in users:
        users[user_id] = {"fund": 0, "keys": []}

    await update.message.reply_text(
        "🔥 Welcome to Key Seller Bot\n"
        "/buy - Buy Key\n"
        "/mykeys - My Keys\n"
        "/balance - Check Fund"
    )

# ---- Buy Key ----
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if len(keys_stock) == 0:
        await update.message.reply_text("❌ Out of stock")
        return

    key = random.choice(keys_stock)
    keys_stock.remove(key)

    users[user_id]["keys"].append(key)

    await update.message.reply_text(f"✅ Purchased Key:\n{key}")

# ---- My Keys ----
async def mykeys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    keys = users.get(user_id, {}).get("keys", [])
    
    if not keys:
        await update.message.reply_text("You have no keys")
        return

    await update.message.reply_text("\n".join(keys))

# ---- Balance ----
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    bal = users.get(user_id, {}).get("fund", 0)
    await update.message.reply_text(f"💰 Balance: {bal}")

# ===== ADMIN ID (CHANGE THIS) =====
ADMIN_ID = 8271376829   # Replace with your Telegram ID

# ===== Add Key =====
async def addkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        return
    
    if context.args:
        key = context.args[0]
        keys_stock.append(key)
        await update.message.reply_text("✅ Key Added")
    else:
        await update.message.reply_text("Send key like:\n/addkey KEY-123")

# ===== Check Stock =====
async def stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    await update.message.reply_text(
        "Stock Keys:\n" + "\n".join(keys_stock)
)

# ---- Main ----
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("buy", buy))
app.add_handler(CommandHandler("mykeys", mykeys))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(CommandHandler("addkey", addkey))
app.add_handler(CommandHandler("stock", stock))

print("Bot Running...")
app.run_polling()
