import os

from pyrogram import filters
from pyrogram.types import CallbackQuery
from pyromod import listen

from app import app
from handlers.upload import USER_FILES

from utils.txt_tools import (
    read_txt,
    write_txt,
    remove_duplicates,
    compress_txt,
    sort_lines,
    reverse_lines,
    replace_text,
    filter_text
)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


async def send_output(query, file_path, file_name):

    await query.message.reply_document(
        document=file_path,
        file_name=file_name,
        caption="✅ TXT Edited Successfully"
    )

    try:
        os.remove(file_path)
    except:
        pass


def get_user_file(user_id):

    if user_id not in USER_FILES:
        return None

    return USER_FILES[user_id]


@app.on_callback_query(filters.regex("^duplicate$"))
async def duplicate_callback(client, query: CallbackQuery):

    file = get_user_file(query.from_user.id)

    if not file:
        return await query.answer(
            "❌ Upload TXT First",
            show_alert=True
        )

    lines = read_txt(file)

    result = remove_duplicates(lines)

    output = os.path.join(
        DOWNLOAD_DIR,
        f"{query.from_user.id}_duplicate.txt"
    )

    write_txt(output, result)

    await send_output(
        query,
        output,
        "duplicate_removed.txt"
    )


@app.on_callback_query(filters.regex("^compress$"))
async def compress_callback(client, query: CallbackQuery):

    file = get_user_file(query.from_user.id)

    if not file:
        return await query.answer(
            "❌ Upload TXT First",
            show_alert=True
        )

    lines = read_txt(file)

    result = compress_txt(lines)

    output = os.path.join(
        DOWNLOAD_DIR,
        f"{query.from_user.id}_compress.txt"
    )

    write_txt(output, result)

    await send_output(
        query,
        output,
        "compressed.txt"
    )
@app.on_callback_query(filters.regex("^sort$"))
async def sort_callback(client, query: CallbackQuery):

    file = get_user_file(query.from_user.id)

    if not file:
        return await query.answer(
            "❌ Upload TXT First",
            show_alert=True
        )

    lines = read_txt(file)

    result = sort_lines(lines)

    output = os.path.join(
        DOWNLOAD_DIR,
        f"{query.from_user.id}_sorted.txt"
    )

    write_txt(output, result)

    await send_output(
        query,
        output,
        "sorted.txt"
    )


@app.on_callback_query(filters.regex("^reverse$"))
async def reverse_callback(client, query: CallbackQuery):

    file = get_user_file(query.from_user.id)

    if not file:
        return await query.answer(
            "❌ Upload TXT First",
            show_alert=True
        )

    lines = read_txt(file)

    result = reverse_lines(lines)

    output = os.path.join(
        DOWNLOAD_DIR,
        f"{query.from_user.id}_reverse.txt"
    )

    write_txt(output, result)

    await send_output(
        query,
        output,
        "reverse.txt"
    )


@app.on_callback_query(filters.regex("^filter_link$"))
async def filter_link_callback(client, query: CallbackQuery):

    file = get_user_file(query.from_user.id)

    if not file:
        return await query.answer(
            "❌ Upload TXT First",
            show_alert=True
        )

    await query.message.reply_text(
        "🔍 Send the text or link to remove from the TXT file."
    )

    msg = await client.listen(query.message.chat.id)

    keyword = msg.text.strip()

    lines = read_txt(file)

    result = filter_text(lines, keyword)

    output = os.path.join(
        DOWNLOAD_DIR,
        f"{query.from_user.id}_filtered.txt"
    )

    write_txt(output, result)

    await send_output(
        query,
        output,
        "filtered.txt"
    )