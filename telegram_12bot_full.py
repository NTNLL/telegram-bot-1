from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
import json
from datetime import datetime

# משתנים גלובליים
ADMIN_ID = 5533574855
authorized_users = []
pending_approvals = {}
category_data = [
    {"name": "מזון", "products": [{"name": "פיצה", "price": 50}, {"name": "ברגר", "price": 30}]},
    {"name": "משקאות", "products": [{"name": "קולה", "price": 10}, {"name": "מיץ", "price": 8}]}
]
categories = [cat["name"] for cat in category_data]

def load_authorized_users():
    global authorized_users
    try:
        with open("authorized_users.json", "r", encoding="utf-8") as f:
            authorized_users = json.load(f)
    except FileNotFoundError:
        authorized_users = []

def save_authorized_users():
    with open("authorized_users.json", "w", encoding="utf-8") as f:
        json.dump(authorized_users, f, ensure_ascii=False, indent=2)

def load_categories():
    global category_data, categories
    try:
        with open("categories.json", "r", encoding="utf-8") as f:
            category_data = json.load(f)
            categories = [cat["name"] for cat in category_data]
    except FileNotFoundError:
        category_data = [
            {"name": "מזון", "products": [{"name": "פיצה", "price": 50}, {"name": "ברגר", "price": 30}]},
            {"name": "משקאות", "products": [{"name": "קולה", "price": 10}, {"name": "מיץ", "price": 8}]}
        ]
        categories = [cat["name"] for cat in category_data]
        save_categories()

def save_categories():
    with open("categories.json", "w", encoding="utf-8") as f:
        json.dump(category_data, f, ensure_ascii=False, indent=2)

def save_order(user_id, product, quantity, address, phone):
    try:
        with open("orders.json", "r", encoding="utf-8") as f:
            orders = json.load(f)
    except FileNotFoundError:
        orders = []
    orders.append({
        "user_id": user_id,
        "product": product,
        "quantity": quantity,
        "address": address,
        "phone": phone,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    with open("orders.json", "w", encoding="utf-8") as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)

def load_reviews():
    try:
        with open("reviews.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_reviews(reviews):
    with open("reviews.json", "w", encoding="utf-8") as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)

def load_button_layout():
    try:
        with open("button_layout.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"layout": "2_per_row"}

def save_button_layout(layout):
    with open("button_layout.json", "w", encoding="utf-8") as f:
        json.dump({"layout": layout}, f, ensure_ascii=False, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    load_categories()
    layout = load_button_layout()["layout"]
    keyboard = build_main_keyboard(layout)
    if chat.id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("👑 תפריט ניהול", callback_data="admin_menu")])
    if update.callback_query:
        await update.callback_query.message.edit_text(
            "❓ פעם ראשונה שמזמינים בבוט?\n"
            "לחץ על כפתור 🛒 *הזמנה ללקוח חדש* כדי להתחיל.\n"
            "אחרי ההזמנה הראשונה תוכל לבצע הזמנה מהירה דרך כפתור 🛍 *הזמנה מהירה* - לקוחות קבועים\n\n"
            "📍 אזור פעילות: תל אביב והסביבה\n"
            "🧾 תפריט: ראה קטגוריות ומוצרים בלחיצה על *קטגוריות ומוצרים*\n\n"
            "תודה שבחרתם לקנות אצלנו ❤️",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "❓ פעם ראשונה שמזמינים בבוט?\n"
            "לחץ על כפתור 🛒 *הזמנה ללקוח חדש* כדי להתחיל.\n"
            "אחרי ההזמנה הראשונה תוכל לבצע הזמנה מהירה דרך כפתור 🛍 *הזמנה מהירה* - לקוחות קבועים\n\n"
            "📍 אזור פעילות: תל אביב והסביבה\n"
            "🧾 תפריט: ראה קטגוריות ומוצרים בלחיצה על *קטגוריות ומוצרים*\n\n"
            "תודה שבחרתם לקנות אצלנו ❤️",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

def build_main_keyboard(layout):
    buttons = [
        InlineKeyboardButton("🛒 הזמנה ללקוח חדש", callback_data="new_order"),
        InlineKeyboardButton("🛍 הזמנה מהירה", callback_data="quick_order"),
        InlineKeyboardButton("👁 צפה בביקורת", callback_data="view_reviews"),
        InlineKeyboardButton("✍️ כתוב ביקורת", callback_data="write_review"),
        InlineKeyboardButton("📦 קטגוריות ומוצרים", callback_data="show_categories")
    ]
    if layout == "1_per_row":
        return [[btn] for btn in buttons]
    elif layout == "2_per_row":
        return [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    elif layout == "3_per_row":
        return [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
    return [buttons]

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    print(f"Button clicked: {data}")
    global reviews, category_data, categories

    if data == "new_order":
        if query.from_user.id in authorized_users:
            await show_categories(update, context)
        else:
            context.user_data.clear()
            context.user_data["awaiting_id"] = True
            await query.message.reply_text("📩 אנא שלח את תעודת הזהות שלך (מספר בלבד)")

    elif data == "show_categories":
        await show_categories(update, context)

    elif data == "back":
        await start(update, context)

    elif data.startswith("approve_") and query.from_user.id == ADMIN_ID:
        user_id = int(data.split("_")[1])
        if user_id not in authorized_users:
            authorized_users.append(user_id)
            save_authorized_users()
            await show_categories(update, context, chat_id=user_id)
        await query.message.reply_text("🟢 המשתמש אושר.")

    elif data.startswith("deny_") and query.from_user.id == ADMIN_ID:
        user_id = int(data.split("_")[1])
        await context.bot.send_message(chat_id=user_id, text="❌ הבקשה נדחתה.")
        await query.message.reply_text("🔴 המשתמש נדחה.")

    elif data == "admin_menu" and query.from_user.id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("📋 צפייה בהזמנות", callback_data="view_orders")],
            [InlineKeyboardButton("🧾 אישורי משתמשים", callback_data="pending_approvals")],
            [InlineKeyboardButton("➕ הוסף קטגוריה", callback_data="add_category")],
            [InlineKeyboardButton("➕ הוסף מוצר לקטגוריה", callback_data="add_product")],
            [InlineKeyboardButton("🗑 מחק ביקורת", callback_data="delete_review")],
            [InlineKeyboardButton("🗑 מחק קטגוריה", callback_data="delete_category")],
            [InlineKeyboardButton("🗑 מחק מוצר", callback_data="delete_product")],
            [InlineKeyboardButton("📝 סדר כפתורים", callback_data="arrange_buttons")],
            [InlineKeyboardButton("⬅️ חזרה", callback_data="back")]
        ]
        await query.edit_message_text(
            "👑 תפריט ניהול:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "arrange_buttons" and query.from_user.id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("1 כפתור בשורה", callback_data="layout_1")],
            [InlineKeyboardButton("2 כפתורים בשורה", callback_data="layout_2")],
            [InlineKeyboardButton("3 כפתורים בשורה", callback_data="layout_3")],
            [InlineKeyboardButton("⬅️ חזרה", callback_data="back")]
        ]
        await query.edit_message_text(
            "📐 בחר סידור כפתורים:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data in ["layout_1", "layout_2", "layout_3"] and query.from_user.id == ADMIN_ID:
        layout = "1_per_row" if data == "layout_1" else "2_per_row" if data == "layout_2" else "3_per_row"
        save_button_layout(layout)
        await query.edit_message_text(
            f"✅ סידור כפתורים שונה ל-{layout.replace('_per_row', ' כפתורים בשורה')}. השינויים יחולו ב-/start חדש."
        )
        await start(update, context)

    elif data == "view_orders" and query.from_user.id == ADMIN_ID:
        try:
            with open("orders.json", "r", encoding="utf-8") as f:
                orders = json.load(f)
        except FileNotFoundError:
            orders = []
        if not orders:
            await query.message.reply_text("📭 אין הזמנות שמורות.")
        else:
            text = "📦 רשימת הזמנות (5 אחרונות):\n\n"
            for o in orders[-5:]:
                text += (
                    f"🕒 {o['time']}\n"
                    f"👤 ID: {o['user_id']}\n"
                    f"📦 מוצר: {o['product']}\n"
                    f"🔢 כמות: {o['quantity']}\n"
                    f"📍 כתובת: {o['address']}\n"
                    f"📞 טלפון: {o['phone']}\n"
                    f"————————————\n"
                )
            await query.message.reply_text(text)

    elif data == "pending_approvals" and query.from_user.id == ADMIN_ID:
        if not pending_approvals:
            await query.message.reply_text("📭 אין בקשות אישור ממתינות.")
        else:
            text = "🧾 בקשות אישור:\n\n"
            for user_id, details in pending_approvals.items():
                text += f"👤 ID: {user_id}\n📄 ת.ז.: {details['id_text']}\n\n"
            await query.message.reply_text(text)

    elif data == "add_category":
        context.user_data["add_step"] = "category_name"
        await query.message.reply_text("📝 כתוב את שם הקטגוריה החדשה:")

    elif data == "add_product":
        if not categories:
            await query.message.reply_text("⚠️ אין קטגוריות זמינות. הוסף קטגוריה קודם.")
        else:
            keyboard = [[InlineKeyboardButton(cat, callback_data=f"add_to_{cat}")] for cat in categories]
            await query.message.reply_text("📦 בחר קטגוריה להוספת מוצר:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("add_to_"):
        cat_name = data.replace("add_to_", "")
        context.user_data["selected_category"] = cat_name
        context.user_data["add_step"] = "product_name"
        await query.message.reply_text("📝 כתוב את שם המוצר:")

    elif data == "quick_order" and query.from_user.id in authorized_users:
        await show_categories(update, context, quick_order=True)

    elif data == "write_review":
        context.user_data["add_step"] = "rating"
        await query.message.reply_text("⭐ אנא הענק דירוג (1-5) לאיכות השירות ואמינות:")

    elif data == "view_reviews":
        global reviews
        reviews = load_reviews()
        if not reviews:
            await query.message.reply_text("📭 אין ביקורות זמינות.")
        else:
            for review in reviews[-5:]:
                user = review.get('user', 'משתמש אנונימי')
                rating = review.get('rating', 0)
                text_content = review.get('text', 'ללא תיאור')
                time_content = review.get('time', datetime.now().strftime("%Y-%m-%d %H:%M"))
                stars = "★" * rating + "☆" * (5 - rating)
                text = f"⭐ ביקורת:\n👤 {user}\n🌟 דירוג: {stars} ({rating}/5)\n📝 {text_content}\n📅 {time_content}"
                keyboard = [
                    [InlineKeyboardButton("🗑 מחק", callback_data=f"delete_review_{reviews.index(review)}")]
                ] if query.from_user.id == ADMIN_ID else [[InlineKeyboardButton("⬅️ חזרה", callback_data="back")]]
                await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("delete_review_") and query.from_user.id == ADMIN_ID:
        index = int(data.replace("delete_review_", ""))
        reviews = load_reviews()
        if 0 <= index < len(reviews):
            deleted_review = reviews.pop(index)
            save_reviews(reviews)
            await query.message.reply_text(f"🗑 ביקורת נמחקה: {deleted_review['text']}")
        else:
            await query.message.reply_text("⚠️ ביקורת לא נמצאה.")

    elif data == "delete_category" and query.from_user.id == ADMIN_ID:
        if not categories:
            await query.message.reply_text("⚠️ אין קטגוריות למחיקה.")
        else:
            keyboard = [[InlineKeyboardButton(cat, callback_data=f"confirm_delete_cat_{cat}")] for cat in categories]
            keyboard.append([InlineKeyboardButton("⬅️ חזרה", callback_data="back")])
            await query.message.reply_text("🗑 בחר קטגוריה למחיקה:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("confirm_delete_cat_") and query.from_user.id == ADMIN_ID:
        cat_name = data.replace("confirm_delete_cat_", "")
        category_data[:] = [cat for cat in category_data if cat["name"] != cat_name]
        save_categories()
        load_categories()  # עדכון רשימת הקטגוריות
        await query.message.reply_text(f"🗑 קטגוריה '{cat_name}' נמחקה בהצלחה.")
        await start(update, context)

    elif data == "delete_product" and query.from_user.id == ADMIN_ID:
        if not categories:
            await query.message.reply_text("⚠️ אין קטגוריות זמינות.")
        else:
            keyboard = [[InlineKeyboardButton(cat, callback_data=f"select_cat_delete_prod_{cat}")] for cat in categories]
            keyboard.append([InlineKeyboardButton("⬅️ חזרה", callback_data="back")])
            await query.message.reply_text("🗑 בחר קטגוריה למחיקת מוצר:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("select_cat_delete_prod_") and query.from_user.id == ADMIN_ID:
        cat_name = data.replace("select_cat_delete_prod_", "")
        category = next((cat for cat in category_data if cat["name"] == cat_name), None)
        if category and category["products"]:
            keyboard = [[InlineKeyboardButton(prod["name"], callback_data=f"confirm_delete_prod_{cat_name}_{prod['name']}")] for prod in category["products"]]
            keyboard.append([InlineKeyboardButton("⬅️ חזרה", callback_data="back")])
            await query.message.reply_text(f"🗑 בחר מוצר למחיקה בקטגוריה {cat_name}:", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.message.reply_text("⚠️ אין מוצרים בקטגוריה זו.")

    elif data.startswith("confirm_delete_prod_") and query.from_user.id == ADMIN_ID:
        parts = data.replace("confirm_delete_prod_", "").split("_")
        cat_name, prod_name = parts[0], parts[1]
        category = next((cat for cat in category_data if cat["name"] == cat_name), None)
        if category:
            category["products"] = [prod for prod in category["products"] if prod["name"] != prod_name]
            save_categories()
            await query.message.reply_text(f"🗑 מוצר '{prod_name}' נמחק מקטגוריה '{cat_name}'.")
        else:
            await query.message.reply_text("⚠️ שגיאה במחיקת המוצר.")
        await start(update, context)

    elif data.startswith("cat_"):
        cat_name = data.replace("cat_", "")
        context.user_data["current_category"] = cat_name
        products = [prod["name"] for prod in next((cat["products"] for cat in category_data if cat["name"] == cat_name), [])]
        keyboard = [[InlineKeyboardButton(prod, callback_data=f"prod_{prod}")] for prod in products]
        if products:
            keyboard.append([InlineKeyboardButton("⬅️ חזרה", callback_data="personal_order")])
        await query.message.reply_text(f"📦 בחר מוצר בקטגוריה {cat_name}:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("prod_"):
        prod_name = data.replace("prod_", "")
        context.user_data["current_product"] = prod_name
        await query.message.reply_text(f"📝 אנא שלח את כמות המוצר '{prod_name}' (מספר):")

    elif data == "personal_order":
        await show_categories(update, context)

async def show_categories(update, context, chat_id=None, quick_order=False):
    query = update.callback_query if hasattr(update, 'callback_query') else None
    load_categories()
    if chat_id:
        chat = await context.bot.get_chat(chat_id)
    else:
        chat = update.effective_chat
    keyboard = [[InlineKeyboardButton(cat, callback_data=f"cat_{cat}")] for cat in categories]
    if quick_order and chat_id in authorized_users:
        keyboard.append([InlineKeyboardButton("✅ אשר הזמנה", callback_data="confirm_quick_order")])
    keyboard.append([InlineKeyboardButton("⬅️ חזרה", callback_data="back")])
    print(f"Showing categories: {keyboard}")
    await chat.send_message("📋 בחר קטגוריה:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    global reviews, category_data

    if context.user_data.get("add_step"):
        step = context.user_data["add_step"]
        if step == "rating":
            try:
                rating = int(user_text)
                if 1 <= rating <= 5:
                    context.user_data["rating"] = rating
                    context.user_data["add_step"] = "review_text"
                    await update.message.reply_text("✍️ כתוב את תיאור הביקורת שלך:")
                else:
                    await update.message.reply_text("⚠️ אנא הזן דירוג בין 1 ל-5.")
            except ValueError:
                await update.message.reply_text("⚠️ אנא הזן מספר תקין בין 1 ל-5.")
        elif step == "review_text":
            user = update.message.from_user.full_name
            review = {
                "user": user,
                "rating": context.user_data.get("rating", 0),
                "text": user_text,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            reviews = load_reviews()
            reviews.append(review)
            save_reviews(reviews)
            context.user_data.clear()
            keyboard = [[InlineKeyboardButton("⬅️ חזרה", callback_data="back")]]
            await update.message.reply_text("⭐ הביקורת נשלחה בהצלחה! תודה!", reply_markup=InlineKeyboardMarkup(keyboard))

    elif context.user_data.get("ordering"):
        order_step = context.user_data["order_step"]
        if order_step == "address":
            context.user_data["address"] = user_text
            context.user_data["order_step"] = "phone"
            await update.message.reply_text("📞 אנא שלח את מספר הטלפון שלך (למשל: 050-1234567):")
        elif order_step == "phone":
            context.user_data["phone"] = user_text
            address = context.user_data["address"]
            phone = context.user_data["phone"]
            product = context.user_data.get("current_product", "לא צוין")
            quantity = context.user_data.get("quantity", "לא צוין")
            await update.message.reply_text(
                f"✅ הזמנה נרשמה!\nמוצר: {product}\nכמות: {quantity}\nכתובת: {address}\nטלפון: {phone}\n"
                "נציג יצור איתך קשר. לחץ /start לחזרה."
            )
            save_order(update.message.from_user.id, product, quantity, address, phone)
            full_name = update.message.from_user.full_name
            username = update.message.from_user.username if update.message.from_user.username else "ללא שם משתמש"
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"📦 הזמנה חדשה!\nמוצר: {product}\nכמות: {quantity}\nכתובת: {address}\nטלפון: {phone}\n"
                     f"מאת: {full_name} (@{username})"
            )
            context.user_data.clear()

    elif context.user_data.get("awaiting_id"):
        context.user_data["id_text"] = user_text
        context.user_data.pop("awaiting_id")
        context.user_data["awaiting_selfie"] = True
        await update.message.reply_text("📸 שלח סלפי עם תעודה מזהה.")

    elif "current_product" in context.user_data:
        try:
            quantity = int(user_text)
            context.user_data["quantity"] = quantity
            context.user_data["ordering"] = True
            context.user_data["order_step"] = "address"
            await update.message.reply_text("📍 אנא שלח את כתובתך (למשל: רחוב, מספר, עיר):")
        except ValueError:
            await update.message.reply_text("❌ אנא שלח מספר תקין לכמות.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    photo_file = update.message.photo[-1].file_id

    if context.user_data.get("awaiting_selfie"):
        selfie_file_id = photo_file
        id_text = context.user_data.get("id_text")
        pending_approvals[user_id] = {"id_text": id_text, "selfie": selfie_file_id}

        buttons = [
            [InlineKeyboardButton("🟢 אשר", callback_data=f"approve_{user_id}"),
             InlineKeyboardButton("❌ דחה", callback_data=f"deny_{user_id}")],
        ]
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"📄 ת.ז. ממשתמש {user_id}: {id_text}")
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=selfie_file_id, caption=f"🤳 סלפי ממשתמש {user_id}",
                                     reply_markup=InlineKeyboardMarkup(buttons))
        context.user_data.clear()
        await update.message.reply_text("✅ התמונות נשלחו. המתן לאישור.")

if __name__ == "__main__":
    load_authorized_users()
    app = ApplicationBuilder().token("7150982630:AAGfZlyNUDLJG8tBVZLzm8wUkAHUbk-dA2g").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("🤖 הבוט פועל!")
    app.run_polling()
