from pyrogram import Client
from vars import API_ID, API_HASH, BOT_TOKEN

app = Client(
    "TxtEditorBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

# Import handlers
from handlers.start import *
from handlers.upload import *
from handlers.callbacks import *

if __name__ == "__main__":
    print("===================================")
    print(" TXT Editor Bot Started Successfully")
    print("===================================")
    app.run()