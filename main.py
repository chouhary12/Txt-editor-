import asyncio
import os
import re
import shutil
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

app = Client("txt_tools_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
states = {}
URL_RE = re.compile(r"(?i)\b(?:https?://|www\.)[^\s<>\[\]{}\"']+")

def safe_filename(name, default="output"):
    name = (name or "").strip()
    name = re.sub(r"[\\/:*?\"<>|\x00-\x1f]", "_", name)
    name = name.strip(" .")
    if not name:
        name = default
    if name.lower().endswith(".txt"):
        name = name[:-4].rstrip(" .") or default
    return name[:120] + ".txt"

def unique(items):
    seen, out = set(), []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out

def urls(lines):
    return unique(m.group(0).strip().rstrip(".,;:!?)]}>\"'") for line in lines for m in URL_RE.finditer(line))

def read_lines(path):
    data = Path(path).read_bytes()
    for enc in ("utf-8", "utf-8-sig", "utf-16", "latin-1"):
        try:
            return data.decode(enc).splitlines()
        except UnicodeDecodeError:
            pass
    return data.decode("utf-8", errors="ignore").splitlines()

async def subscribed(client, user_id):
    try:
        member = await client.get_chat_member(FORCE_SUB_CHANNEL, user_id)
        return getattr(member, "status", "") not in ("left", "kicked", "banned")
    except (UserNotParticipant, ChatAdminRequired):
        return False
    except Exception:
        return False

def sub_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Channel", url=FORCE_SUB_URL)],
        [InlineKeyboardButton("🔄 Check Subscription", callback_data="checksub")]
    ])

async def need_sub(client, message):
    if await subscribed(client, message.from_user.id):
        return True
    await message.reply_text(
        "🔒 **Please join our channel first.**\n\nAfter joining, tap **Check Subscription**.",
        reply_markup=sub_markup()
    )
    return False

def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔎 New Links", callback_data="compare"),
         InlineKeyboardButton("🔗 Extract URLs", callback_data="extract")],
        [InlineKeyboardButton("🧹 Clean TXT", callback_data="clean"),
         InlineKeyboardButton("📊 TXT Stats", callback_data="stats")],
        [InlineKeyboardButton("🔀 Merge TXT", callback_data="merge"),
         InlineKeyboardButton("♻️ Duplicates", callback_data="duplicates")],
        [InlineKeyboardButton("📝 Text → TXT", callback_data="texttxt")]
    ])

@app.on_message(filters.command("start"))
async def start(client, message):
    if not await need_sub(client, message): return
    await message.reply_text(
        "👋 **TXT Tools Bot**\n\nChoose a TXT tool:",
        reply_markup=menu()
    )

@app.on_message(filters.command("help"))
async def help_cmd(client, message):
    if not await need_sub(client, message): return
    await message.reply_text(
        "/compare - OLD vs NEW, return new URLs\n"
        "/extract - extract URLs\n"
        "/clean - remove blank/duplicate lines\n"
        "/stats - TXT statistics\n"
        "/merge - merge two TXT files\n"
        "/duplicates - find duplicate lines\n"
        "/texttxt - convert text to TXT file\n\n"
        f"Max file size: {MAX_FILE_MB} MB"
    )

async def begin(client, message, action):
    if not await need_sub(client, message): return
    states[message.from_user.id] = {"action": action, "files": []}
    prompts = {
        "compare": "📁 Send **OLD TXT** first.",
        "extract": "📁 Send TXT file.",
        "clean": "📁 Send TXT file.",
        "stats": "📁 Send TXT file.",
        "merge": "📁 Send the **first TXT** file.",
        "duplicates": "📁 Send TXT file.",
        "texttxt": "📝 Send the text you want to convert into a TXT file."
    }
    await message.reply_text(prompts[action])

for command, action in [
    ("compare", "compare"), ("extract", "extract"), ("clean", "clean"),
    ("stats", "stats"), ("merge", "merge"), ("duplicates", "duplicates"),
    ("texttxt", "texttxt")
]:
    @app.on_message(filters.command(command))
    async def command_handler(client, message, _action=action):
        await begin(client, message, _action)

@app.on_callback_query(filters.regex("^checksub$"))
async def checksub(client, callback):
    if await subscribed(client, callback.from_user.id):
        await callback.message.edit_text("✅ Subscription verified!\n\nUse /start")
    else:
        await callback.answer("❌ Join the channel first.", show_alert=True)

@app.on_callback_query(filters.regex("^(compare|extract|clean|stats|merge|duplicates|texttxt)$"))
async def menu_callback(client, callback):
    if not await subscribed(client, callback.from_user.id):
        await callback.message.edit_text("🔒 Join the channel first.", reply_markup=sub_markup())
        return
    action = callback.data
    states[callback.from_user.id] = {"action": action, "files": []}
    await callback.message.edit_text({
        "compare": "📁 Send **OLD TXT** first.",
        "extract": "📁 Send TXT file.",
        "clean": "📁 Send TXT file.",
        "stats": "📁 Send TXT file.",
        "merge": "📁 Send the **first TXT** file.",
        "duplicates": "📁 Send TXT file.",
        "texttxt": "📝 Send the text you want to convert into a TXT file."
    }[action])

@app.on_message(filters.text & ~filters.command(["start", "help", "compare", "extract", "clean", "stats", "merge", "duplicates", "texttxt"]))
async def text_handler(client, message):
    if not await need_sub(client, message): return
    state = states.get(message.from_user.id)
    if not state:
        return

    action = state.get("action")

    if action == "texttxt":
        # First text message becomes the file content; next message is the filename.
        if not state.get("text_content"):
            state["text_content"] = message.text
            await message.reply_text(
                "📄 **Text received!**\n\n"
                "Ab file ka naam bhejo.\n"
                "Example: `My Lectures` or `My Lectures.txt`"
            )
            state["action"] = "texttxt_filename"
            return

    if action == "texttxt_filename":
        filename = safe_filename(message.text, "converted")
        content = state.get("text_content", "")
        tmp = Path(tempfile.mkdtemp(prefix="txtbot_"))
        try:
            out = tmp / filename
            out.write_text(content, encoding="utf-8")
            await message.reply_document(str(out), caption=f"✅ TXT created: `{filename}`")
        finally:
            states.pop(message.from_user.id, None)
            shutil.rmtree(tmp, ignore_errors=True)
        return

    if action == "compare_filename":
        filename = safe_filename(message.text, "new_links")
        result = state.get("result_lines", [])
        tmp = Path(tempfile.mkdtemp(prefix="txtbot_"))
        try:
            out = tmp / filename
            out.write_text("\n".join(result) + ("\n" if result else ""), encoding="utf-8")
            await message.reply_document(
                str(out),
                caption=f"✅ New unique links: {len(result)}\n📝 Name + link preserved\n📄 File: `{filename}`"
            )
        finally:
            states.pop(message.from_user.id, None)
            shutil.rmtree(tmp, ignore_errors=True)
        return


@app.on_message(filters.document)
async def document_handler(client, message):
    if not await need_sub(client, message): return
    state = states.get(message.from_user.id)
    if not state:
        await message.reply_text("ℹ️ Use /start first.")
        return

    doc = message.document
    name = doc.file_name or "file.txt"
    if not name.lower().endswith(".txt"):
        await message.reply_text("❌ Only .txt files are allowed.")
        return
    if (doc.file_size or 0) > MAX_FILE_BYTES:
        await message.reply_text(f"❌ Maximum file size is {MAX_FILE_MB} MB.")
        return

    status = await message.reply_text("⏳ Processing...")
    tmp = Path(tempfile.mkdtemp(prefix="txtbot_"))
    path = tmp / name

    try:
        await message.download(file_name=str(path))
        lines = read_lines(path)
        action = state["action"]

        if action == "compare":
            if not state.get("old_lines"):
                state["old_lines"] = lines
                await status.edit_text("✅ OLD file received. Now send **NEW TXT**.")
                return

            # Compare by URL, but preserve the complete original NEW line
            # (lecture/name + URL) in the output.
            old_url_set = set(urls(state["old_lines"]))
            result = []
            seen_new = set()
            for line in lines:
                found = list(URL_RE.finditer(line))
                if not found:
                    continue
                link = found[0].group(0).strip().rstrip(".,;:!?)]}>\"'")
                if link not in old_url_set and link not in seen_new:
                    result.append(line)
                    seen_new.add(link)

            # Ask for a custom output filename; keep the result in memory
            # because the current temp folder is cleaned after this handler.
            state["result_lines"] = result
            state["action"] = "compare_filename"
            await status.edit_text(
                f"✅ Found **{len(result)}** new unique links.\n\n"
                "📄 Ab output file ka naam bhejo.\n"
                "Example: `New Links` or `New Links.txt`"
            )
            return

        elif action == "extract":
            result = urls(lines)
            out = tmp / "extracted_urls.txt"
            out.write_text("\n".join(result) + ("\n" if result else ""), encoding="utf-8")
            await message.reply_document(str(out), caption=f"🔗 URLs: {len(result)}")

        elif action == "clean":
            result = unique(x.strip() for x in lines if x.strip())
            out = tmp / "cleaned.txt"
            out.write_text("\n".join(result) + ("\n" if result else ""), encoding="utf-8")
            await message.reply_document(str(out), caption=f"🧹 Clean lines: {len(result)}")

        elif action == "stats":
            nonempty = [x.strip() for x in lines if x.strip()]
            uniq = len(set(nonempty))
            await status.edit_text(
                "📊 **TXT Stats**\n\n"
                f"Total lines: `{len(lines)}`\n"
                f"Non-empty: `{len(nonempty)}`\n"
                f"Unique lines: `{uniq}`\n"
                f"Duplicate lines: `{len(nonempty)-uniq}`\n"
                f"Unique URLs: `{len(urls(lines))}`\n"
                f"Words: `{sum(len(x.split()) for x in lines)}`\n"
                f"Characters: `{sum(len(x) for x in lines)}`"
            )
            states.pop(message.from_user.id, None)
            return

        elif action == "merge":
            if not state.get("first_lines"):
                state["first_lines"] = lines
                await status.edit_text("✅ First file received. Now send **second TXT**.")
                return
            merged = list(state["first_lines"]) + list(lines)
            out = tmp / "merged.txt"
            out.write_text("\n".join(merged) + ("\n" if merged else ""), encoding="utf-8")
            await message.reply_document(str(out), caption=f"🔀 Merged lines: {len(merged)}")

        elif action == "duplicates":
            counts = {}
            for line in lines:
                v = line.strip()
                if v: counts[v] = counts.get(v, 0) + 1
            result = unique(v for v in (x.strip() for x in lines) if v and counts[v] > 1)
            out = tmp / "duplicates.txt"
            out.write_text("\n".join(result) + ("\n" if result else ""), encoding="utf-8")
            await message.reply_document(str(out), caption=f"♻️ Duplicate unique lines: {len(result)}")

        states.pop(message.from_user.id, None)
        await status.delete()

    except Exception as e:
        states.pop(message.from_user.id, None)
        await status.edit_text(f"❌ Error: `{type(e).__name__}`\n`{str(e)[:500]}`")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    print("TXT Tools Bot starting...")
    app.run()
