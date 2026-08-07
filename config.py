import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Bot Settings
BOT_NAME = "TXT Compare Bot"

# Folder
DOWNLOAD_DIR = "downloads"
OUTPUT_DIR = "outputs"

# Admin (Optional)
ADMIN_IDS = [
    # Example:
    # 123456789
]

# Max file size (1GB)
MAX_FILE_SIZE = 1024 * 1024 * 1024