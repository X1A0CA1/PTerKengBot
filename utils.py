import contextlib
import datetime

import pytz
import os
import log

from pyrogram.types import Message
from pyrogram.enums import ChatMembersFilter
from pyrogram.enums import ChatType

from scheduler import scheduler
from config import TIME_ZONE, WORK_CHAT, ADMINS, INFO_DELETE_TIME
from PterKengBot import bot


async def _delete_message(message) -> bool:
    with contextlib.suppress(Exception):
        await message.delete()
        return True
    return False


def add_delete_message_job(message: Message, time: int) -> None:
    scheduler.add_job(
        _delete_message,
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

    if from_user_id in ADMINS:
        return True

    if sender_chat_id == WORK_CHAT:
        return True

    chat_admin_lst = []
    async for m in bot.get_chat_members(WORK_CHAT, filter=ChatMembersFilter.ADMINISTRATORS):
        if m.user.is_bot:
            continue
        chat_admin_lst.append(m.user.id)

    if from_user_id in chat_admin_lst:
        return True

    return False


def _contains_only_special_whitespace(string: str) -> bool:
    chars = (
        "\u000A\u0020\u200B\u200C\u200D\u200E\u200F\u2060\u2061\u2062\u2063\u2064\u2065\u2066"
        "\u2068\u2069\u206A\u206B\u206C\u206D\u206E\u206F\u3164\uFE0F"
    )
    return all(char in chars for char in string)


async def get_user_fullname_from_user_id(user: int) -> str:
    user = await bot.get_users(user)
    full_name = user.first_name
    if user.last_name:
        full_name += f" {user.last_name}"
    return full_name


async def get_sender_user_fullname_from_message(message: Message) -> str:
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
        full_name = await get_sender_user_fullname_from_message(message)
        user_id = message.from_user.id
    elif message.sender_chat:
        full_name = await get_sender_chat_fullname_from_message(message)
        user_id = message.sender_chat.id
    else:
        return None, None
    return full_name, user_id


async def get_chat_title_and_id_from_message(message: Message) -> tuple[None, None] | tuple[str, int]:
    if message.chat.type in [ChatType.CHANNEL, ChatType.SUPERGROUP, ChatType.GROUP]:
        chat_title = message.chat.title
        chat_id = message.chat.id
    elif message.chat.type in [ChatType.BOT, ChatType.PRIVATE]:
        chat_title = await get_sender_user_fullname_from_message(message)
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


async def check_required(message, admin_required=False, work_group_required=False) -> bool:
    if work_group_required and not await check_work_group(message):
        await log.not_work_group_log(message)
        await reply_and_delay_delete(message, "请在猫站群内使用该命令", INFO_DELETE_TIME)
        return False

    if admin_required and not await check_permission(message):
        await log.no_permission_log(message)
        await reply_and_delay_delete(message, "你没有权限使用该命令", INFO_DELETE_TIME)
        return False

    return True


async def get_ids_from_link(link: str) -> (int, int):
    link = link.replace('telegram.me', 't.me')
    link = link.replace('telegram.dog', 't.me')
    link = link.replace('https://', '')
    link = link.replace('http://', '')
    if link.find('t.me') == -1:
        return None, None

    chat_id = None
    message_id: int = 0
    # https://t.me/c/114514/1  # CHANNEL
    # https://t.me/114514/1  # GROUP

    if link.find('/c/') != -1:
        my_strs = link.split('/c/')
        if len(my_strs) < 2:
            return None, None
        my_strs = my_strs[1].split('/')
        if len(my_strs) < 2:
            return None, None
        chat_id = int('-100' + my_strs[0])
        message_id = int(my_strs[1])
    else:
        my_strs = link.split('/')
        if len(my_strs) < 3:
            return None, None
        chat_id = my_strs[1]
        if chat_id.isdigit():
            chat_id = int(f'-100{chat_id}')
        message_id = int(my_strs[2])

    if not chat_id or not message_id:
        return None, None

    return chat_id, message_id
