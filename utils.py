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

    if message.from_user:
        user = await bot.get_chat_member(WORK_CHAT, from_user_id)
        if user.custom_title:
            return True

    if from_user_id in ADMINS or sender_chat_id == WORK_CHAT:
        return True
    return False


