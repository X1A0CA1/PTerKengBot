import contextlib
import datetime
import pytz

from pyrogram.types import Message

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


async def get_chat_fullname_from_message(message: Message) -> str:
    full_name = message.chat.title
    if message.author_signature:
        if _contains_only_special_whitespace(message.author_signature):
            full_name += "(空白字符皮套人)"
        else:
            full_name += f"({message.author_signature})"
    else:
        full_name += "(无头衔皮套人)"
    return full_name
