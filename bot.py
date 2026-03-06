import random
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ===== CONFIG =====
TOKEN = "8758244481:AAFvmUcNNrmMKDgp3hqX1osX58ApYomC3n0"
ADMIN_ID = 8271376829

# ===== DATABASE =====
users = {}
keys_stock = ["KEY-111", "KEY-222", "KEY-333"]

fund_requests = {}
earnings = 0


# ================= MAIN MENU =================
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Buy Key", callback_data="buy")],
        [InlineKeyboardButton("💰 Add Fund", callback_data="fund_menu")],
        [InlineKeyboardButton("📜 Purchase History", callback_data="history")],
        [InlineKeyboardButton("💰 Balance", callback_data="balance")]
    ])


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in users:
        users[user_id] = {
            "fund": 0,
            "history": []
        }

        try:
            await context.bot.send_message(
                ADMIN_ID,
                f"🆕 New User Joined\nID: {user_id}"
            )
        except:
            pass

    await update.message.reply_text(
        "🔥 Welcome To Seller Store",
        reply_markup=main_menu()
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

    time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    users[user_id]["history"].append(
        f"Purchased {key} | {time_now}"
    )

    await query.message.reply_text(f"✅ Your Key:\n{key}")


# ================= FUND MENU =================
async def fund_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
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


# ================= FUND REQUEST =================
async def fund_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    amount = int(query.data.split("_")[1])
    user_id = query.from_user.id

    fund_requests[user_id] = amount

    await query.message.reply_text(
        "📩 Send payment screenshot to admin.\nWait for approval."
    )

    # Forward request to admin
    await context.bot.send_message(
        ADMIN_ID,
        f"💰 Fund Request\nUser: {user_id}\nAmount: {amount}\n\n"
        f"Approve: /approve {user_id}\nReject: /reject {user_id}"
    )


# ================= BUTTON HANDLER =================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "buy":
        await buy(update, context)

    elif data == "fund_menu":
        await fund_menu(update, context)

    elif data.startswith("fund_"):
        await fund_amount(update, context)

    elif data == "history":
        user_id = query.from_user.id

        hist = users.get(user_id, {}).get("history", [])

        await query.message.reply_text(
            "\n".join(hist) if hist else "No History"
        )

    elif data == "balance":
        user_id = query.from_user.id
        bal = users.get(user_id, {}).get("fund", 0)

        await query.message.reply_text(f"💰 Balance: {bal}")

    elif data == "back":
        await query.message.reply_text(
            "Main Menu",
            reply_markup=main_menu()
        )


# ================= ADMIN APPROVE =================
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if context.args:
        user_id = int(context.args[0])

        if user_id in fund_requests:
            amount = fund_requests[user_id]

            users[user_id]["fund"] += amount

            await context.bot.send_message(
                user_id,
                f"✅ Fund Added\nAmount: {amount}"
            )

            await update.message.reply_text("✅ Approved")


# ================= ADMIN REJECT =================
async def reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if context.args:
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
app.run_polling()
