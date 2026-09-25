import asyncio
import os
import re
import tempfile
from pathlib import Path

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from pyrogram.errors import UserNotParticipant, ChatAdminRequired

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

FORCE_SUB_CHANNEL = os.getenv("FORCE_SUB_CHANNEL", "@inventor_king_24")
FORCE_SUB_URL = os.getenv("FORCE_SUB_URL", "https://t.me/inventor_king_24")
MAX_FILE_MB = int(os.getenv("MAX_FILE_MB", "20"))
MAX_FILE_BYTES = MAX_FILE_MB * 1024 * 1024

app = Client(
    "txt_tools_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

# Per-user temporary workflow state. Keep worker=1 for this simple in-memory flow.
user_states = {}

URL_RE = re.compile(
    r"(?i)\b(?:https?://|www\.)[^\s<>\[\]{}\"']+"
)

def normalize_url(url: str) -> str:
    return url.strip().rstrip(".,;:!?)]}>\"'")

def read_lines(path: str):
    data = Path(path).read_bytes()
    for enc in ("utf-8", "utf-8-sig", "utf-16", "latin-1"):
        try:
            return data.decode(enc).splitlines()
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="ignore").splitlines()

def extract_urls(lines):
    return [normalize_url(m.group(0)) for line in lines for m in URL_RE.finditer(line)]

def unique_preserve(items):
    seen = set()
    out = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out

def clean_lines(lines):
    return unique_preserve(
        line.strip() for line in lines
        if line.strip()
    )

async def is_subscribed(client: Client, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(FORCE_SUB_CHANNEL, user_id)
        status = getattr(member, "status", "")
        return status not in ("left", "kicked", "banned")
    except UserNotParticipant:
        return False
    except (ChatAdminRequired, Exception):
        # If the bot cannot verify the membership, fail closed so force-sub
        # remains enforceable. The exact exception is intentionally not exposed.
        return False

def force_sub_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Channel", url=FORCE_SUB_URL)],
        [InlineKeyboardButton("🔄 Check Subscription", callback_data="checksub")],
    ])

async def require_sub(client: Client, message: Message) -> bool:
    if await is_subscribed(client, message.from_user.id):
        return True
    await message.reply_text(
        "🔒 **Please join our channel first.**\n\n"
        "After joining, tap **Check Subscription**.",
        reply_markup=force_sub_markup(),
    )
    return False

def menu_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔎 New Links", callback_data="menu_compare"),
         InlineKeyboardButton("🔗 Extract URLs", callback_data="menu_extract")],
        [InlineKeyboardButton("🧹 Clean TXT", callback_data="menu_clean"),
         InlineKeyboardButton("📊 TXT Stats", callback_data="menu_stats")],
        [InlineKeyboardButton("🔀 Merge TXT", callback_data="menu_merge"),
         InlineKeyboardButton("♻️ Find Duplicates", callback_data="menu_dupes")],
    ])

@app.on_message(filters.command("start"))
async def start(_, message: Message):
    if not await require_sub(_, message):
        return
    await message.reply_text(
        "👋 **TXT Tools Bot**\n\n"
        "TXT files ke saath kaam karne ke liye option choose karein:\n\n"
        "🔎 **New Links** — Old TXT ke mukable New TXT ke naye links\n"
        "🔗 **Extract URLs** — TXT se URLs nikaalo\n"
        "🧹 **Clean TXT** — Blank lines + duplicate lines remove\n"
        "📊 **TXT Stats** — Lines, URLs, duplicates, words, chars\n"
        "🔀 **Merge TXT** — 2 TXT files merge\n"
        "♻️ **Find Duplicates** — Duplicate lines alag file me",
        reply_markup=menu_markup(),
    )

@app.on_message(filters.command("help"))
async def help_cmd(client, message: Message):
    if not await require_sub(client, message):
        return
    await message.reply_text(
        "📚 **Commands**\n\n"
        "/start - Main menu\n"
        "/compare - Old + New TXT se new links\n"
        "/extract - TXT se URLs extract\n"
        "/clean - TXT clean\n"
        "/stats - TXT statistics\n"
        "/merge - 2 TXT merge\n"
        "/duplicates - Duplicate lines\n\n"
        f"📦 Max file size: {MAX_FILE_MB} MB"
    )

async def begin(client, message, action):
    if not await require_sub(client, message):
        return
    user_states[message.from_user.id] = {"action": action, "files": []}
    prompts = {
        "compare": "📁 **Compare mode**\nPehle **OLD TXT** file bhejo.",
        "extract": "📁 TXT file bhejo jisme se URLs extract karne hain.",
        "clean": "📁 Clean karne wali TXT file bhejo.",
        "stats": "📁 Statistics ke liye TXT file bhejo.",
        "merge": "📁 Pehli TXT file bhejo, phir doosri.",
        "duplicates": "📁 Duplicate lines find karne ke liye TXT file bhejo.",
    }
    await message.reply_text(prompts[action])

@app.on_message(filters.command("compare"))
async def compare_cmd(client, message):
    await begin(client, message, "compare")

@app.on_message(filters.command("extract"))
async def extract_cmd(client, message):
    await begin(client, message, "extract")

@app.on_message(filters.command("clean"))
async def clean_cmd(client, message):
    await begin(client, message, "clean")

@app.on_message(filters.command("stats"))
async def stats_cmd(client, message):
    await begin(client, message, "stats")

@app.on_message(filters.command("merge"))
async def merge_cmd(client, message):
    await begin(client, message, "merge")

@app.on_message(filters.command("duplicates"))
async def duplicates_cmd(client, message):
    await begin(client, message, "duplicates")

@app.on_callback_query(filters.regex("^checksub$"))
async def checksub(client, callback: CallbackQuery):
    if await is_subscribed(client, callback.from_user.id):
        await callback.message.edit_text(
            "✅ Subscription verified!\n\n/start dabao aur bot use karo."
        )
    else:
        await callback.answer("❌ Pehle channel join karo.", show_alert=True)

@app.on_callback_query(filters.regex("^menu_"))
async def menu_callback(client, callback: CallbackQuery):
    if not await is_subscribed(client, callback.from_user.id):
        await callback.message.edit_text(
            "🔒 Please join the channel first.",
            reply_markup=force_sub_markup(),
        )
        return
    action = callback.data.replace("menu_", "")
    if action == "compare":
        action = "compare"
    elif action == "extract":
        action = "extract"
    elif action == "clean":
        action = "clean"
    elif action == "stats":
        action = "stats"
    elif action == "merge":
        action = "merge"
    elif action == "dupes":
        action = "duplicates"
    user_states[callback.from_user.id] = {"action": action, "files": []}
    prompts = {
        "compare": "📁 Pehle **OLD TXT** file bhejo.",
        "extract": "📁 TXT file bhejo.",
        "clean": "📁 TXT file bhejo.",
        "stats": "📁 TXT file bhejo.",
        "merge": "📁 Pehli TXT file bhejo.",
        "duplicates": "📁 TXT file bhejo.",
    }
    await callback.message.edit_text(prompts[action])

@app.on_message(filters.document)
async def document_handler(client, message: Message):
    if not await require_sub(client, message):
        return

    user_id = message.from_user.id
    state = user_states.get(user_id)
    if not state:
        await message.reply_text("ℹ️ Pehle /start ya koi command use karo.")
        return

    doc = message.document
    filename = doc.file_name or "file.txt"
    if not filename.lower().endswith(".txt"):
        await message.reply_text("❌ Sirf `.txt` file allowed hai.")
        return
    if (doc.file_size or 0) > MAX_FILE_BYTES:
        await message.reply_text(f"❌ File limit {MAX_FILE_MB} MB hai.")
        return

    status = await message.reply_text("⏳ File process ho rahi hai...")
    tmp_dir = Path(tempfile.mkdtemp(prefix="txtbot_"))
    input_path = tmp_dir / filename

    try:
        await message.download(file_name=str(input_path))
        lines = read_lines(input_path)
        action = state["action"]

        if action == "compare":
            state["files"].append(str(input_path))
            if len(state["files"]) == 1:
                await status.edit_text("✅ OLD file mil gayi.\n📁 Ab **NEW TXT** file bhejo.")
                return

            old_lines = read_lines(state["files"][0])
            new_lines = lines
            old_urls = set(extract_urls(old_lines))
            new_urls = unique_preserve(extract_urls(new_lines))
            result = [u for u in new_urls if u not in old_urls]
            out = tmp_dir / "new_links.txt"
            out.write_text("\n".join(result) + ("\n" if result else ""), encoding="utf-8")
            await message.reply_document(
                str(out),
                caption=f"✅ **New links:** {len(result)}\n"
                        f"Old unique URLs: {len(old_urls)}\n"
                        f"New unique URLs: {len(new_urls)}"
            )
            user_states.pop(user_id, None)

        elif action == "extract":
            result = unique_preserve(extract_urls(lines))
            out = tmp_dir / "extracted_urls.txt"
            out.write_text("\n".join(result) + ("\n" if result else ""), encoding="utf-8")
            await message.reply_document(str(out), caption=f"🔗 Extracted unique URLs: {len(result)}")
            user_states.pop(user_id, None)

        elif action == "clean":
            result = clean_lines(lines)
            out = tmp_dir / "cleaned.txt"
            out.write_text("\n".join(result) + ("\n" if result else ""), encoding="utf-8")
            await message.reply_document(str(out), caption=f"🧹 Cleaned lines: {len(result)}")
            user_states.pop(user_id, None)

        elif action == "stats":
            stripped = [x.strip() for x in lines]
            nonempty = [x for x in stripped if x]
            unique_count = len(set(nonempty))
            dup_count = len(nonempty) - unique_count
            urls = unique_preserve(extract_urls(lines))
            words = sum(len(x.split()) for x in lines)
            chars = sum(len(x) for x in lines)
            await status.edit_text(
                "📊 **TXT Statistics**\n\n"
                f"Total lines: `{len(lines)}`\n"
                f"Non-empty lines: `{len(nonempty)}`\n"
                f"Unique lines: `{unique_count}`\n"
                f"Duplicate lines: `{dup_count}`\n"
                f"Unique URLs: `{len(urls)}`\n"
                f"Words: `{words}`\n"
                f"Characters: `{chars}`"
            )
            user_states.pop(user_id, None)

        elif action == "merge":
            state["files"].append(str(input_path))
            if len(state["files"]) == 1:
                await status.edit_text("✅ First file mil gayi.\n📁 Ab **second TXT** file bhejo.")
                return
            merged = []
            for p in state["files"]:
                merged.extend(read_lines(p))
            out = tmp_dir / "merged.txt"
            out.write_text("\n".join(merged) + ("\n" if merged else ""), encoding="utf-8")
            await message.reply_document(str(out), caption=f"🔀 Merged lines: {len(merged)}")
            user_states.pop(user_id, None)

        elif action == "duplicates":
            counts = {}
            for line in lines:
                value = line.strip()
                if value:
                    counts[value] = counts.get(value, 0) + 1
            dupes = [line for line in clean_lines(lines) if counts.get(line, 0) > 1]
            out = tmp_dir / "duplicates.txt"
            out.write_text("\n".join(dupes) + ("\n" if dupes else ""), encoding="utf-8")
            await message.reply_document(str(out), caption=f"♻️ Duplicate unique lines: {len(dupes)}")
            user_states.pop(user_id, None)

        await status.delete()

    except Exception as exc:
        user_states.pop(user_id, None)
        await status.edit_text(f"❌ Processing error: `{type(exc).__name__}`")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.on_message(filters.text & ~filters.command(["start", "help", "compare", "extract", "clean", "stats", "merge", "duplicates"]))
async def text_fallback(client, message):
    if not await require_sub(client, message):
        return
    await message.reply_text("ℹ️ TXT file upload karo ya /start se option choose karo.")

if __name__ == "__main__":
    print("TXT Tools Bot starting...")
    app.run()
