from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from bot import app


@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):

    text = (
        "👋 **Welcome to TXT Editor Bot**\n\n"
        "📄 Mujhe ek .txt file bhejo.\n"
        "Uske baad jis operation ka button dabaoge, "
        "main edited TXT file wapas bhej dunga.\n\n"
        "✅ Available Features:\n"
        "• Duplicate Remove\n"
        "• Link Replace\n"
        "• Link Filter\n"
        "• TXT Compress\n"
        "• Sort Lines\n"
        "• Reverse Lines\n"
        "• Add Prefix\n"
        "• Add Suffix\n"
        "• Find & Replace\n"
        "• Line Counter"
    )

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📄 Send TXT File",
                    callback_data="send_txt"
                )
            ],
            [
                InlineKeyboardButton(
                    "ℹ️ Help",
                    callback_data="help"
                ),
                InlineKeyboardButton(
                    "👨‍💻 About",
                    callback_data="about"
                )
            ]
        ]
    )

    await message.reply_text(
        text=text,
        reply_markup=buttons
    )