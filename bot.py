import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

PRODUCTS = {
    "lindt": {
        "name": "🍫 Lindt Schokolade",
        "options": [
            ("2", 15.00),
            ("3", 20.00),
            ("5", 40.00),
        ],
    },
    "ice": {
        "name": "🧊 Clear Ice",
        "options": [
            ("0,5", 40.00),
            ("1", 70.00),
            ("2,5", 150.00),
        ],
    },
    "bonbon": {
        "name": "🍬 Bonbon",
        "options": [
            ("1", 10.00),
            ("3", 20.00),
            ("5", 40.00),
        ],
    },
}


def main_menu():
    keyboard = [
        [InlineKeyboardButton("🍫 Lindt Schokolade", callback_data="cat_lindt")],
        [InlineKeyboardButton("🧊 Clear Ice", callback_data="cat_ice")],
        [InlineKeyboardButton("🍬 Bonbon", callback_data="cat_bonbon")],
        [InlineKeyboardButton("🛒 Warenkorb", callback_data="cart")],
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🛒 Willkommen bei Dz Shop!\n\n"
        "Willkommen in unserem Online-Shop.\n\n"
        "Bitte wählen Sie eine Kategorie:"
    )

    await update.message.reply_text(
        text,
        reply_markup=main_menu()
    )


async def category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    category_id = query.data.replace("cat_", "")
    product = PRODUCTS[category_id]

    keyboard = []

    for index, (amount, price) in enumerate(product["options"]):
        keyboard.append([
            InlineKeyboardButton(
                f"{amount} — {price:.2f} €",
                callback_data=f"select_{category_id}_{index}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton("⬅️ Zurück", callback_data="home")
    ])

    await query.edit_message_text(
        f"{product['name']}\n\n"
        "Bitte wählen Sie eine Menge:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def select_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, category_id, index = query.data.split("_")
    index = int(index)

    product = PRODUCTS[category_id]
    amount, price = product["options"][index]

    keyboard = [
        [
            InlineKeyboardButton(
                "🛒 In den Warenkorb",
                callback_data=f"add_{category_id}_{index}"
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ Zurück",
                callback_data=f"cat_{category_id}"
            )
        ],
    ]

    text = (
        f"{product['name']}\n\n"
        f"Menge: {amount}\n"
        f"Preis: {price:.2f} €\n"
    )

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("✅ Zum Warenkorb hinzugefügt!")

    _, category_id, index = query.data.split("_")
    index = int(index)

    product = PRODUCTS[category_id]
    amount, price = product["options"][index]

    cart = context.user_data.setdefault("cart", [])

    cart.append({
        "product": product["name"],
        "amount": amount,
        "price": price,
    })

    keyboard = [
        [
            InlineKeyboardButton(
                "🛒 Warenkorb",
                callback_data="cart"
            )
        ],
        [
            InlineKeyboardButton(
                "🛍 Weiter einkaufen",
                callback_data="home"
            )
        ],
    ]

    await query.edit_message_text(
        f"✅ Zum Warenkorb hinzugefügt!\n\n"
        f"{product['name']}\n"
        f"Menge: {amount}\n"
        f"Preis: {price:.2f} €",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    cart_items = context.user_data.get("cart", [])

    if not cart_items:
        await query.edit_message_text(
            "🛒 Ihr Warenkorb ist leer.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    "🛍 Produkte ansehen",
                    callback_data="home"
                )]
            ])
        )
        return

    total = sum(item["price"] for item in cart_items)

    lines = ["🛒 Warenkorb\n"]

    for item in cart_items:
        lines.append(
            f"{item['product']}\n"
            f"Menge: {item['amount']} — {item['price']:.2f} €\n"
        )

    lines.append(f"💰 Gesamt: {total:.2f} €")

    keyboard = [
        [InlineKeyboardButton(
            "🗑 Warenkorb leeren",
            callback_data="clear"
        )],
        [InlineKeyboardButton(
            "🛍 Weiter einkaufen",
            callback_data="home"
        )],
        [InlineKeyboardButton(
            "✅ Bestellung bestätigen",
            callback_data="checkout"
        )],
    ]

    await query.edit_message_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def clear_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("🗑 Warenkorb geleert.")

    context.user_data["cart"] = []

    await query.edit_message_text(
        "🛒 Ihr Warenkorb ist leer.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "🛍 Produkte ansehen",
                callback_data="home"
            )]
        ])
    )


async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    cart_items = context.user_data.get("cart", [])

    if not cart_items:
        await query.edit_message_text("🛒 Ihr Warenkorb ist leer.")
        return

    total = sum(item["price"] for item in cart_items)

    await query.edit_message_text(
        "✅ Bestellung vorbereitet!\n\n"
        f"💰 Gesamt: {total:.2f} €\n\n"
        "Vielen Dank für Ihre Bestellung!"
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data

    if data.startswith("cat_"):
        await category(update, context)

    elif data.startswith("select_"):
        await select_product(update, context)

    elif data.startswith("add_"):
        await add_to_cart(update, context)

    elif data == "cart":
        await cart(update, context)

    elif data == "clear":
        await clear_cart(update, context)

    elif data == "checkout":
        await checkout(update, context)

    elif data == "home":
        await home(update, context)


async def home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "🛒 Willkommen bei Dz Shop!\n\n"
        "Bitte wählen Sie eine Kategorie:",
        reply_markup=main_menu()
    )


def main():
    token = os.environ.get("BOT_TOKEN")

    if not token:
        raise RuntimeError("BOT_TOKEN fehlt.")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Dz Shop Bot läuft...")
    app.run_polling()


if __name__ == "__main__":
    main()
