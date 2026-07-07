import os

from pyrogram import filters
from pyrogram.types import Message

from bot import app

# User ki latest uploaded file
USER_FILES = {}

# Download folder
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


@app.on_message(filters.document & filters.private)
async def upload_txt(client, message: Message):

    document = message.document

    # Sirf .txt allow
    if not document.file_name.lower().endswith(".txt"):
        return await message.reply_text(
            "❌ Please send only .txt files."
        )

    file_path = os.path.join(
        DOWNLOAD_DIR,
        f"{message.from_user.id}_{document.file_name}"
    )

    await message.download(file_name=file_path)

    USER_FILES[message.from_user.id] = file_path

    await message.reply_text(
        f"✅ TXT uploaded successfully!\n\n"
        f"📄 File: `{document.file_name}`\n\n"
        f"Ab operation select karo."
    )