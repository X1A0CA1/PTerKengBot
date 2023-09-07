from pyrogram import Client, filters
from pyrogram.types import Message

from scheduler import scheduler
from config import WORK_CHAT, LOG_CHAT
from utils import check_required
import log

user_forwarding_enabled = {}


@scheduler.scheduled_job("interval", seconds=3600)
async def clean_forwarding_dict():
    global user_forwarding_enabled
    for key in list(user_forwarding_enabled.keys()):
        del user_forwarding_enabled[key]
        await Client.send_message(key, "消息转发已自动关闭")


@Client.on_message(filters.command("forward_mode", prefixes="/"))
async def reply_mode_command(_, message):
    await check_required(message, admin_required=True)
    user_id = message.from_user.id
    command = message.text.lower().split()[1]
    if command == "on":
        user_forwarding_enabled[user_id] = True
        await message.reply(f"消息转发已启用，您发送的所有消息都将转发到{WORK_CHAT}")
    elif command == "off":
        try:
            del user_forwarding_enabled[user_id]
        except KeyError:
            pass
        await message.reply("消息转发已关闭")

    await log.command_log(message, "#RAN_FORWARD_MODE", f"{message.text}")


@Client.on_message(filters.private & ~filters.me & filters.text)
async def forward_message(_, message: Message):
    await check_required(message, admin_required=True)
    user_id = message.from_user.id
    if user_id in user_forwarding_enabled and user_forwarding_enabled[user_id]:
        await message.copy(chat_id=WORK_CHAT)
        await message.forward(chat_id=LOG_CHAT)
