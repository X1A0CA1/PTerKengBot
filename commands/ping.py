from datetime import datetime

from pyrogram.raw.functions import Ping
from pyrogram import Client, filters

from utils import edit_and_delay_delete


@Client.on_message(filters.command('ping'))
async def ping_message(bot, message):
    start = datetime.now()
    await bot.invoke(Ping(ping_id=0))
    end = datetime.now()
    ping_duration = (end - start).microseconds / 1000
    start = datetime.now()
    message = await message.reply("Poi~", disable_notification=True)
    end = datetime.now()
    msg_duration = (end - start).microseconds / 1000
    await edit_and_delay_delete(
        message,
        f"Poi~ | 服务器延迟: {ping_duration}ms | 消息延迟: {msg_duration}ms",
        10
    )
