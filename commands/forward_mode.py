import pytz
import datetime
import pyromod

from pyrogram import Client, filters
from pyrogram.types import Message

from scheduler import scheduler
from config import WORK_CHAT, LOG_CHAT, TIME_ZONE
from utils import check_required
from PterKengBot import bot
import log

user_forwarding_enabled = {}


async def _auto_close_forwarding_mode(key) -> bool:
    global user_forwarding_enabled
    try:
        del user_forwarding_enabled[key]
        await bot.send_message(chat_id=key, text="消息转发已自动关闭")
        await log.info(
            log_tag="#FORWARDING_CLEAN",
            log_summaries=f"{key} 的消息转发已自动关闭"
        )
    except KeyError:
        pass
    return True


def add_close_forwarding_job(key, time: int) -> None:
    scheduler.add_job(
        _auto_close_forwarding_mode,
        "date",
        id=f"close_forwarding_mode|{key}",
        name=f"close_forwarding_mode|{key}",
        args=[key],
        run_date=datetime.datetime.now(pytz.timezone(TIME_ZONE)) + datetime.timedelta(seconds=time),
        replace_existing=True,
    )


@Client.on_message(filters.command("forward_mode", prefixes="/") & filters.private & ~filters.me, group=0)
async def reply_mode_command(_, message):
    await check_required(message, admin_required=True)
    await log.command_log(message, "#RAN_FORWARD_MODE", f"{message.text}")
    user_id = message.from_user.id
    parameter = message.text.split()
    if len(parameter) != 2:
        await message.reply("参数错误。用法： /forward_mode on|off")
        return
    if parameter[1] == "on":
        user_forwarding_enabled[user_id] = True
        await message.reply(f"消息转发已启用，您发送的所有消息都将转发到 {WORK_CHAT}，1 小时后自动关闭。")
        add_close_forwarding_job(user_id, 3600)
    elif parameter[1] == "off":
        try:
            del user_forwarding_enabled[user_id]
        except KeyError:
            pass
        await message.reply("消息转发已关闭")


@Client.on_message(filters.command("edit", prefixes="/") & filters.private & ~filters.me, group=0)
async def edit_message(_, message):
    await check_required(message, admin_required=True)
    await log.command_log(message, "#RAN_EDIT_COMMAND", f"{message.text}")
    parameter = message.text.split()
    if parameter < 2:
        await message.reply("参数错误。用法： /edit <msg_link> <text>")
        return
    try:
        msg_link = parameter[1]
        text = " ".join(parameter[2:])
        target_chat_id = msg_link.split("/")[-2]
        target_message_id = msg_link.split("/")[-1]
        await bot.edit_message_text(chat_id=target_chat_id, message_id=target_message_id, text=text)
        await message.reply("消息已编辑")
    except Exception as e:
        await message.reply(f"编辑失败：{e}")


@Client.on_message(filters.command("reply", prefixes="/") & filters.private & ~filters.me, group=0)
async def reply_message(_, message):
    await check_required(message, admin_required=True)
    await log.command_log(message, "#RAN_REPLY_COMMAND", f"{message.text}")
    parameter = message.text.split()
    if parameter < 1:
        await message.reply("参数错误。用法： /delete <msg_link>")
        return
    try:
        msg = await message.ask("请输入回复内容：")
        msg_link = parameter[1]
        target_chat_id = msg_link.split("/")[-2]
        target_message_id = msg_link.split("/")[-1]
        await msg.copy(chat_id=target_chat_id, reply_to_message_id=target_message_id)
        await msg.forward(chat_id=LOG_CHAT)
        await bot.send_reaction(message.chat.id, message.id, "👍")
    except Exception as e:
        await message.reply(f"回复失败：{e}")


@Client.on_message(filters.command("delete", prefixes="/") & filters.private & ~filters.me, group=0)
async def delete_message(_, message):
    await check_required(message, admin_required=True)
    await log.command_log(message, "#RAN_DELETE_COMMAND", f"{message.text}")
    parameter = message.text.split()
    if parameter < 1:
        await message.reply("参数错误。用法： /delete <msg_link>")
        return
    try:
        msg_link = parameter[1]
        target_chat_id = msg_link.split("/")[-2]
        target_message_id = msg_link.split("/")[-1]
        await bot.delete_messages(chat_id=target_chat_id, message_ids=target_message_id)
        await bot.send_reaction(message.chat.id, message.id, "👍")
    except Exception as e:
        await message.reply(f"删除失败：{e}")


@Client.on_message(filters.private & ~filters.me & ~filters.regex(r"^/"), group=99)
async def forward_message(_, message: Message):
    await check_required(message, admin_required=True)
    user_id = message.from_user.id
    if user_id in user_forwarding_enabled and user_forwarding_enabled[user_id]:
        await message.copy(chat_id=WORK_CHAT)
        await message.forward(chat_id=LOG_CHAT)
        await bot.send_reaction(message.chat.id, message.id, "👍")
