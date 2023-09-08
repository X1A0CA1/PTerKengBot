from datetime import datetime

import log
from utils import edit_and_delay_delete
from config import INFO_DELETE_TIME

from pyrogram.raw.functions import Ping
from pyrogram import Client, filters


@Client.on_message(filters.command('ping'), group=0)
async def ping_message(bot, message):
    start = datetime.now()
    await bot.invoke(Ping(ping_id=0))
    end = datetime.now()
    ping_duration = (end - start).microseconds / 1000
    start = datetime.now()
    waiting_for_edit_message = await message.reply("Poi~", disable_notification=True)
    end = datetime.now()
    msg_duration = (end - start).microseconds / 1000
    await edit_and_delay_delete(
        waiting_for_edit_message,
        f"Poi~ | 服务器延迟: {ping_duration}ms | 消息延迟: {msg_duration}ms",
        INFO_DELETE_TIME
    )
    await log.command_log(message, "#RAN_COMMAND_PING", "执行/ping")
