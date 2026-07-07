import os

from pyrogram import Client
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from pyrogram import filters

from bot import app
from handlers.upload import USER_FILES


@app.on_callback_query()
async def callbacks(client: Client, query: CallbackQuery):

    user_id = query.from_user.id
    data = query.data

    if data == "send_txt":
        return await query.message.edit_text(
            "📄 Please send your TXT file."
        )

    elif data == "help":
        return await query.message.edit_text(
            "**Help**\n\n"
            "1. Send a TXT file.\n"
            "2. Select an operation.\n"
            "3. Receive the edited TXT."
        )

    elif data == "about":
        return await query.message.edit_text(
            "**TXT Editor Bot**\n"
            "Made with Pyrogram 2.x"
        )

    if user_id not in USER_FILES:
        return await query.answer(
            "❌ First upload a TXT file.",
            show_alert=True
        )

    menu = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🗑 Duplicate Remove",
                    callback_data="duplicate"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔄 Replace Link",
                    callback_data="replace_link"
                ),
                InlineKeyboardButton(
                    "🚫 Filter Link",
                    callback_data="filter_link"
                )
            ],
            [
                InlineKeyboardButton(
                    "📦 Compress",
                    callback_data="compress"
                ),
                InlineKeyboardButton(
                    "🔤 Sort",
                    callback_data="sort"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔁 Reverse",
                    callback_data="reverse"
                )
            ]
        ]
    )

    await query.message.reply_text(
        "Choose an operation:",
        reply_markup=menu
    )