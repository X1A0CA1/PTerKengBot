from pyrogram import Client, filters
from pyrogram.errors import UserNotParticipant
from pyrogram.enums import ChatMemberStatus

import commands.pter_place
import log
from config import LOG_CHAT, WORK_CHAT, NOTIFY_CHAT, NOTIFY_CHAT_INVITE_LINK, INVITE_LINK_DELETE_TIME, ADMINS
from PterKengBot import bot
from utils import reply_and_delay_delete, check_required, get_user_fullname_from_user_id
from scheduler import scheduler

STICKER_FOR_HAS_PLACE = "BQACAgUAAx0ETaitjQABDrVbZC7-CyRnP9bNWyL6uyQTsEZYmhUAAgIIAAKBgXlVI9gBrugVVmAeBA"
STICKER_FOR_NO_PLACE = "BQACAgUAAx0ETaitjQABDrVcZC7-DHoDQxTig8mGKF4tXTtDjZUAAgMIAAKBgXlVIUkm6W3k8YseBA"


async def need_notify():
    pter_place = commands.pter_place.PTER_PLACE
    if pter_place is None:
        return None
    if len(pter_place) <= 2:
        return None
    if pter_place[-1] == pter_place[-2]:
        return None
    if pter_place[-1] > 0 >= pter_place[-2]:
        return True
    elif pter_place[-1] <= 0 < pter_place[-2]:
        return False
    else:
        return None


async def send_notify_message(text, sticker):
    try:
        await bot.send_message(chat_id=NOTIFY_CHAT, text=text)
        await bot.send_message(chat_id=LOG_CHAT, text=text)
        await bot.send_document(
            WORK_CHAT,
            sticker
        )
    except Exception as e:
        await log.error(
            log_tag="#NOTIFY_ERROR",
            log_summaries="通知时出现了问题:",
            more_log_text=f"{e}\n\n 通知消息: \n{text}"
        )


async def send_notify():
    need_to_notify = await need_notify()
    if need_to_notify is None:
        return
    if need_to_notify is True:
        text = f"有坑了\n\n{await commands.pter_place.get_place_message()}"
        await send_notify_message(text, STICKER_FOR_HAS_PLACE)
    elif need_to_notify is False:
        text = f"坑无了"
        await send_notify_message(text, STICKER_FOR_NO_PLACE)


@Client.on_message(filters.command('notice_me'), group=0)
async def notice_me(_, message):
    # TODO 重写 notice_me，生成邀请链接，私聊发送邀请链接，使用/超出时间限制后销毁。
    if await check_required(message, work_group_required=True):
        await reply_and_delay_delete(message, f"请加入通知频道~ \n{NOTIFY_CHAT_INVITE_LINK}", INVITE_LINK_DELETE_TIME)
        await log.command_log(message, "#RAN_COMMAND_NOTICE_ME", "执行/notice_me")


async def kick_users_if_not_in_work_group():
    kicked_users = []

    async for member in bot.get_chat_members(NOTIFY_CHAT):
        if member.status is not ChatMemberStatus.MEMBER:
            continue
        if member.user.id in ADMINS:
            continue
        try:
            await bot.get_chat_member(WORK_CHAT, member.user.id)
        except UserNotParticipant:
            await bot.ban_chat_member(NOTIFY_CHAT, member.user.id)
            kicked_users.append(member.user)
    return kicked_users


async def scheduled_kick_users():
    kicked_users = await kick_users_if_not_in_work_group()
    if not kicked_users:
        return

    more_log_text = "踢出的用户：\n"
    for user in kicked_users:
        more_log_text += f"{user.id} | {await get_user_fullname_from_user_id(user.id)}\n"

    await log.info(
        log_tag="#KICK_USERS_IF_NOT_IN_WORK_GROUP",
        log_summaries=f"有 {len(kicked_users)} 位用户不在猫站群组中，已经踢出",
        more_log_text=more_log_text
    )


@scheduler.scheduled_job("interval", hours=6)
async def scheduled_kick_users_job():
    await scheduled_kick_users()
