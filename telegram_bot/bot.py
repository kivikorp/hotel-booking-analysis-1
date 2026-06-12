import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_BOT_TOKEN_HERE")
API_URL = "https://hotel-booking-analysis-1.onrender.com/bookings/"
STREAMLIT_URL = "https://your-streamlit-url.streamlit.app"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
}

HOTEL_STATE, LEAD_TIME_STATE = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [InlineKeyboardButton("📊 View Project Notebook", url=STREAMLIT_URL)],
        [
            InlineKeyboardButton(
                "📄 Page 1: Fetch Bookings (GET)", callback_data="menu_get"
            )
        ],
        [
            InlineKeyboardButton(
                "➕ Page 2: Add Custom Booking (POST)", callback_data="menu_post"
            )
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(
            "🏨 *Hotel Booking Data Center*\nChoose an option:",
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )
    else:
        await update.callback_query.edit_message_text(
            "🏨 *Hotel Booking Data Center*\nChoose an option:",
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )

    return ConversationHandler.END


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "menu_main":
        return await start(update, context)

    elif query.data == "menu_get":
        try:
            response = requests.get(f"{API_URL}?limit=2", headers=HEADERS)
            if response.status_code == 200:
                data = response.json()
                text = f"**Latest 2 Records from API:**\n\n"
                for i, row in enumerate(data):
                    text += f"Record {i + 1}: {row['hotel']}, Lead Time: {row['lead_time']}, ADR: ${row.get('adr', 0)}\n"
            else:
                text = f"Error fetching data. Code: {response.status_code}"
        except Exception as e:
            text = f"API offline. Error: {e}"

        back_button = [
            [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_main")]
        ]
        await query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(back_button),
            parse_mode="Markdown",
        )
        return ConversationHandler.END

    elif query.data == "menu_post":
        await query.edit_message_text(
            "Let's create a custom booking!\n\nPlease type the **Hotel Type** (e.g., `City Hotel` or `Resort Hotel`):",
            parse_mode="Markdown",
        )
        return HOTEL_STATE


async def hotel_step(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["hotel"] = update.message.text
    await update.message.reply_text(
        "Got it! Now type the **Lead Time** in days (e.g., `45`):",
        parse_mode="Markdown",
    )
    return LEAD_TIME_STATE


async def lead_time_step(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        lead_time = int(update.message.text)
    except ValueError:
        await update.message.reply_text(
            "Please enter a valid number for Lead Time (e.g. 45)."
        )
        return LEAD_TIME_STATE

    hotel = context.user_data["hotel"]

    payload = {
        "hotel": hotel,
        "is_canceled": 0,
        "lead_time": lead_time,
        "stays_in_weekend_nights": 1,
        "stays_in_week_nights": 2,
        "adults": 2,
        "children": 0.0,
        "babies": 0,
        "adr": 120.0,
        "total_of_special_requests": 1,
    }

    try:
        response = requests.post(API_URL, json=payload, headers=HEADERS)
        if response.status_code == 200:
            text = f"✅ **Successfully added custom booking!**\n\n**Hotel:** {hotel}\n**Lead Time:** {lead_time} days\n\nThe datasets have been updated."
        else:
            text = f"❌ Failed to add booking. Code: {response.status_code}"
    except Exception as e:
        text = f"API is offline. Error: {e}"

    keyboard = [
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_main")]
    ]
    await update.message.reply_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Custom booking canceled.")
    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(button_handler),
        ],
        states={
            HOTEL_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, hotel_step)],
            LEAD_TIME_STATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, lead_time_step)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()
