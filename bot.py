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

TOKEN = "8758244481:AAFvmUcNNrmMKDgp3hqX1osX58ApYomC3n0"
ADMIN_ID = 8271376829

users = {}
keys_stock = []
pending_funds = {}
admin_waiting = {}

# ================= MAIN MENU =================
def main_menu():
    keyboard = [
        [InlineKeyboardButton("🛒 Buy Key", callback_data="buy")],
        [InlineKeyboardButton("💰 Add Fund", callback_data="addfund")],
        [InlineKeyboardButton("📜 Purchase History", callback_data="history")],
        [InlineKeyboardButton("💰 Balance", callback_data="balance")]
    ]
    return InlineKeyboardMarkup(keyboard)


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in users:
        users[user_id] = {"fund": 0, "history": []}

    await update.message.reply_text(
        "🌟 Welcome to Premium Key Store\nBuy hacks / keys safely.",
        reply_markup=main_menu()
    )


# ================= ADMIN PANEL =================
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    keyboard = [
        [InlineKeyboardButton("➕ Add Key", callback_data="admin_add")],
        [InlineKeyboardButton("📦 Stock", callback_data="admin_stock")],
        [InlineKeyboardButton("➖ Remove Key", callback_data="admin_remove")]
    ]

    await update.message.reply_text(
        "🔧 Admin Control Panel",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ================= BUTTON HANDLER =================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    # BUY KEY
    if data == "buy":

        if users[user_id]["fund"] < 10:
            await query.message.reply_text("❌ You need at least 10 balance")
            return

        if not keys_stock:
            await query.message.reply_text("❌ Stock empty")
            return

        users[user_id]["fund"] -= 10

        key = random.choice(keys_stock)
        keys_stock.remove(key)

        users[user_id]["history"].append(
            f"{key} | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )

        await query.message.reply_text(f"✅ Key Delivered:\n{key}")

    # ADD FUND
    elif data == "addfund":

        await query.message.reply_photo(
            photo=open("qr.jpg", "rb"),
            caption="💰 Add Fund\n\nMinimum: 30\nMaximum: 500\n\nSend amount then send payment screenshot."
        )

    # HISTORY
    elif data == "history":

        hist = users.get(user_id, {}).get("history", [])

        if not hist:
            await query.message.reply_text("No purchase history.")
        else:
            await query.message.reply_text("\n".join(hist))

    # BALANCE
    elif data == "balance":

        bal = users.get(user_id, {}).get("fund", 0)
        await query.message.reply_text(f"💰 Balance: {bal}")

    # ================= ADMIN =================

    elif data == "admin_add":

        if user_id != ADMIN_ID:
            return

        admin_waiting["mode"] = "add"
        await query.message.reply_text("Send key to add")

    elif data == "admin_remove":

        if user_id != ADMIN_ID:
            return

        admin_waiting["mode"] = "remove"
        await query.message.reply_text("Send key to remove")

    elif data == "admin_stock":

        if user_id != ADMIN_ID:
            return

        if not keys_stock:
            await query.message.reply_text("Stock empty")
            return

        text = "📦 Stock:\n\n"

        for k in keys_stock:
            text += k + "\n"

        text += f"\nTotal: {len(keys_stock)}"

        await query.message.reply_text(text)

    # ================= APPROVE PAYMENT =================

    elif data.startswith("approve_"):

        if user_id != ADMIN_ID:
            return

        uid = int(data.split("_")[1])

        if uid not in pending_funds:
            return

        amount = pending_funds[uid]

        users.setdefault(uid, {"fund": 0, "history": []})
        users[uid]["fund"] += amount

        await context.bot.send_message(
            uid,
            f"✅ Payment Approved\n💰 {amount} added to your balance"
        )

        await context.bot.send_message(
            ADMIN_ID,
            f"Payment approved for {uid}"
        )

        del pending_funds[uid]

        await query.message.delete()

    elif data.startswith("reject_"):

        if user_id != ADMIN_ID:
            return

        uid = int(data.split("_")[1])

        if uid not in pending_funds:
            return

        await context.bot.send_message(uid, "❌ Payment rejected")

        del pending_funds[uid]

        await query.message.delete()


# ================= MESSAGE HANDLER =================
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.from_user.id

    # ADMIN KEY ADD/REMOVE
    if user_id == ADMIN_ID and "mode" in admin_waiting:

        key = update.message.text

        if admin_waiting["mode"] == "add":

            keys_stock.append(key)

            await update.message.reply_text(f"✅ Key Added\n{key}")

        elif admin_waiting["mode"] == "remove":

            if key in keys_stock:
                keys_stock.remove(key)
                await update.message.reply_text("❌ Key removed")
            else:
                await update.message.reply_text("Key not found")

        admin_waiting.clear()
        return

    # FUND AMOUNT
    if update.message.text and update.message.text.isdigit():

        amount = int(update.message.text)

        if amount < 30 or amount > 500:
            await update.message.reply_text("Amount must be between 30 and 500")
            return

        pending_funds[user_id] = amount

        await update.message.reply_text("Now send payment screenshot.")

        await context.bot.send_message(
            ADMIN_ID,
            f"💰 Fund Request\nUser: {user_id}\nAmount: {amount}"
        )

    # SCREENSHOT
    elif update.message.photo and user_id in pending_funds:

        amount = pending_funds[user_id]

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
            ]
        ])

        await context.bot.send_photo(
            ADMIN_ID,
            photo=update.message.photo[-1].file_id,
            caption=f"Payment Screenshot\nUser: {user_id}\nAmount: {amount}",
            reply_markup=keyboard
        )

        await update.message.reply_text("Screenshot sent to admin.")


# ================= MAIN =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("admin", admin))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))

print("Bot Running...")
app.run_polling()
