import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN", "7984580376:AAGXzVhb2U_M9AbTvoSITlVw0Bm9bB17_Bg")
API_URL = "https://hotel-booking-analysis-1.onrender.com"
STREAMLIT_URL = "https://hotel-booking-analysis-1-fuqscrvruww9ugsiqn2fmm.streamlit.app/"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton(
                "📊 View Project Notebook (Streamlit)", url=STREAMLIT_URL
            )
        ],
        [
            InlineKeyboardButton(
                "📄 Page 1: Fetch Latest Bookings (GET)", callback_data="menu_get"
            )
        ],
        [
            InlineKeyboardButton(
                "➕ Page 2: Add Sample Booking (POST)", callback_data="menu_post"
            )
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🏨 *Hotel Booking Data Center*\nUse the menu below to navigate the project features:",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    back_button = [
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_main")]
    ]

    if query.data == "menu_main":
        keyboard = [
            [
                InlineKeyboardButton(
                    "📊 View Project Notebook (Streamlit)", url=STREAMLIT_URL
                )
            ],
            [
                InlineKeyboardButton(
                    "📄 Page 1: Fetch Latest Bookings (GET)", callback_data="menu_get"
                )
            ],
            [
                InlineKeyboardButton(
                    "➕ Page 2: Add Sample Booking (POST)", callback_data="menu_post"
                )
            ],
        ]
        await query.edit_message_text(
            "🏨 *Hotel Booking Data Center*\nChoose an option:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

    elif query.data == "menu_get":
        try:
            response = requests.get(f"{API_URL}?limit=2")
            if response.status_code == 200:
                data = response.json()
                text = f"**Latest 2 Records from API:**\n\n"
                for i, row in enumerate(data):
                    text += f"Record {i + 1}: {row['hotel']}, Lead Time: {row['lead_time']}, ADR: ${row.get('adr', 0)}\n"
            else:
                text = "Error fetching data from API."
        except Exception:
            text = "API is currently offline or unreachable."

        await query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(back_button),
            parse_mode="Markdown",
        )

    elif query.data == "menu_post":
        try:
            payload = {"hotel": "City Hotel", "lead_time": 45, "adr": 150.0}
            response = requests.post(API_URL, json=payload)
            if response.status_code == 200:
                text = "✅ Successfully added new booking via POST!\n\nThe Cleaned CSV and Extended CSV have both been updated."
            else:
                text = "❌ Failed to add booking."
        except Exception:
            text = "API is currently offline or unreachable."

        await query.edit_message_text(
            text=text, reply_markup=InlineKeyboardMarkup(back_button)
        )


def main() -> None:
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.run_polling()


if __name__ == "__main__":
    main()
