import contextlib
import datetime
from typing import Tuple

import pytz
import os

from pyrogram.types import Message
from pyrogram.enums.chat_type import ChatType

from scheduler import scheduler
from config import TIME_ZONE, WORK_CHAT, ADMINS
from PterKengBot import bot


async def delete_message(message) -> bool:
    with contextlib.suppress(Exception):
        await message.delete()
        return True
    return False


def add_delete_message_job(message: Message, time: int) -> None:
    scheduler.add_job(
        delete_message,
        "date",
        id=f"{message.chat.id}|{message.id}|delete_message",
        name=f"{message.chat.id}|{message.id}|delete_message",
        args=[message],
        run_date=datetime.datetime.now(pytz.timezone(TIME_ZONE)) + datetime.timedelta(seconds=time),
        replace_existing=True,
    )


async def delay_delete(message: Message, time: int = 10) -> None:
    add_delete_message_job(message, time)


async def edit_and_delay_delete(message: Message, text: str, time: int = 10) -> None:
    await message.edit(text)
    add_delete_message_job(message, time)


async def reply_and_delay_delete(message: Message, text: str, time: int = 10) -> None:
    message = await message.reply(text)
    add_delete_message_job(message, time)


async def check_work_group(message: Message) -> bool:
    if message.chat.id == WORK_CHAT:
        return True
    return False


async def check_permission(message: Message) -> bool:
    from_user_id = message.from_user.id if message.from_user else None
    sender_chat_id = message.sender_chat.id if message.sender_chat else None

    if from_user_id is not None:
        user = await bot.get_chat_member(WORK_CHAT, from_user_id)
        if user.custom_title:
            return True

    if from_user_id in ADMINS or sender_chat_id == WORK_CHAT:
        return True
    return False


def _contains_only_special_whitespace(string: str) -> bool:
    chars = (
        "\u000A\u0020\u200B\u200C\u200D\u200E\u200F\u2060\u2061\u2062\u2063\u2064\u2065\u2066"
        "\u2068\u2069\u206A\u206B\u206C\u206D\u206E\u206F\u3164\uFE0F"
    )
    return all(char in chars for char in string)


async def get_user_fullname_from_message(message: Message) -> str:
    full_name = None
    user = message.from_user
    if user.first_name:
        full_name = user.first_name
    if user.last_name:
        full_name += f" {user.last_name}"
    if _contains_only_special_whitespace(full_name):
        full_name = "某空白名字哥们儿"
    return full_name


async def get_sender_chat_fullname_from_message(message: Message) -> str:
    full_name = message.sender_chat.title
    if message.author_signature:
        if _contains_only_special_whitespace(message.author_signature):
            full_name += "(空白字符皮套人)"
        else:
            full_name += f"({message.author_signature})"
    else:
        full_name += ("(频道皮套)" if message.sender_chat.type is ChatType.CHANNEL else "(无头衔群组皮套)")
    return full_name


async def get_fullname_and_user_id_from_message(message: Message) -> tuple[None, None] | tuple[str, int]:
    if message.from_user:
        full_name = await get_user_fullname_from_message(message)
        user_id = message.from_user.id
    elif message.sender_chat:
        full_name = await get_sender_chat_fullname_from_message(message)
        user_id = message.sender_chat.id
    else:
        return None, None
    return full_name, user_id


async def get_chat_tilte_and_id_from_message(message: Message) -> tuple[None, None] | tuple[str, int]:
    if message.chat.type in [ChatType.CHANNEL, ChatType.SUPERGROUP, ChatType.GROUP]:
        chat_title = message.chat.title
        chat_id = message.chat.id
    elif message.chat.type in [ChatType.BOT, ChatType.PRIVATE]:
        chat_title = await get_user_fullname_from_message(message)
        chat_id = message.chat.id
    else:
        return None, None
    return chat_title, chat_id


def _length_check(text: str) -> bool:
    return len(text) <= 4000


async def send_message_with_length_check(chat_id, text, log_summaries=None) -> Message:
    if _length_check(text):
        message = await bot.send_message(chat_id, text, disable_web_page_preview=True)
    else:
        file_path = "tmp.txt"
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(text)
        message = await bot.send_document(
            chat_id=chat_id,
            document=file_path,
            caption=f"{log_summaries}\n\n消息过长，已经发送为文件"
        )
        os.remove(file_path)
    return message


async def reply_message_with_length_check(message, text) -> Message:
    if _length_check(text):
        message = await message.reply(text, disable_web_page_preview=True)
    else:
        file_path = "tmp.txt"
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(text)
        message = await bot.send_document(
            chat_id=message.chat.id,
            document=file_path,
            caption=f"消息过长，已经发送为文件",
            reply_to_message_id=message.id
        )
        os.remove(file_path)
    return message
