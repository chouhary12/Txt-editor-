from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

app = Client(
    "TxtEditorBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

import handlers.start
import handlers.upload
import handlers.callbacks
import handlers.editor

if __name__ == "__main__":
    print("TXT Editor Bot Started...")
    app.run()