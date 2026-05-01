import requests
from uuid import uuid4
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

from config import *
from database import *

product_map = {}

def headers():
    return {"Authorization": f"Bearer {API_KEY}"}

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("🛒 Products", callback_data="products")],
        [InlineKeyboardButton("💰 Balance", callback_data="balance")]
    ]

    if update.effective_user.id == ADMIN_ID:
        kb.append([InlineKeyboardButton("⚙️ Admin", callback_data="admin")])

    await update.message.reply_text("🚀 PakVaultX Bot", reply_markup=InlineKeyboardMarkup(kb))

# ===== FETCH PRODUCTS =====
def fetch_products():
    products = []
    r = requests.get(f"{BASE_URL}?action=products", headers=headers())

    for p in r.json():
        p["active"] = True
        products.append(p)

    save_products(products)
    return products

# ===== PRODUCTS =====
async def products(update, context):
    q = update.callback_query
    await q.answer()

    global product_map
    product_map = {}

    items = get_products() or fetch_products()

    kb = []
    for p in items:
        if p.get("active", True):
            pid = str(p["id"])
            product_map[pid] = p

            kb.append([
                InlineKeyboardButton(
                    f"{p['name']} - Rs {p['price'] + 50}",
                    callback_data=f"buy_{pid}"
                )
            ])

    await q.message.reply_text("📦 Products:", reply_markup=InlineKeyboardMarkup(kb))

# ===== BUY =====
async def buy(update, context):
    q = update.callback_query
    await q.answer()

    pid = q.data.split("_")[1]
    p = product_map.get(pid)

    if not p:
        await q.message.reply_text("❌ Product not found")
        return

    res = requests.post(
        f"{BASE_URL}?action=order",
        headers=headers(),
        json={
            "product_id": p["id"],
            "quantity": 1,
            "external_order_id": str(uuid4())
        }
    ).json()

    await q.message.reply_text(f"✅ Order:\n{res}")

# ===== BALANCE =====
async def balance(update, context):
    q = update.callback_query
    await q.answer()

    r = requests.get(f"{BASE_URL}?action=balance", headers=headers())
    await q.message.reply_text(f"💰 Balance:\n{r.json()}")

# ===== ADMIN =====
async def admin(update, context):
    q = update.callback_query
    await q.answer()

    kb = [[InlineKeyboardButton("📦 Toggle Products", callback_data="toggle")]]
    await q.message.reply_text("⚙️ Admin Panel", reply_markup=InlineKeyboardMarkup(kb))

async def toggle(update, context):
    q = update.callback_query
    await q.answer()

    items = get_products()

    kb = []
    for p in items:
        status = "✅" if p.get("active", True) else "❌"
        kb.append([
            InlineKeyboardButton(f"{p['name']} {status}", callback_data=f"t_{p['id']}")
        ])

    await q.message.reply_text("Toggle Products:", reply_markup=InlineKeyboardMarkup(kb))

async def toggle_action(update, context):
    q = update.callback_query
    await q.answer()

    pid = q.data.split("_")[1]
    toggle_product(pid)

    await q.message.reply_text("Updated!")

# ===== ROUTER =====
async def router(update, context):
    data = update.callback_query.data

    if data == "products":
        await products(update, context)

    elif data.startswith("buy_"):
        await buy(update, context)

    elif data == "balance":
        await balance(update, context)

    elif data == "admin":
        await admin(update, context)

    elif data == "toggle":
        await toggle(update, context)

    elif data.startswith("t_"):
        await toggle_action(update, context)

# ===== RUN =====
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(router))

print("Bot Running...")
app.run_polling()
