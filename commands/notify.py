from pyrogram import Client, filters

import commands.pter_place
import log
from config import LOG_CHAT, WORK_CHAT, NOTIFY_CHAT, NOTIFY_CHAT_INVITE_LINK, INVITE_LINK_DELETE_TIME
from PterKengBot import bot
from utils import reply_and_delay_delete

STICKER_FOR_HAS_PLACE = "BQACAgUAAx0ETaitjQABDrVbZC7-CyRnP9bNWyL6uyQTsEZYmhUAAgIIAAKBgXlVI9gBrugVVmAeBA"
STICKER_FOR_NO_PLACE = "BQACAgUAAx0ETaitjQABDrVcZC7-DHoDQxTig8mGKF4tXTtDjZUAAgMIAAKBgXlVIUkm6W3k8YseBA"


async def need_notify():
    pter_place = commands.pter_place.PTER_PLACE
    if pter_place is None:
        return
    if len(pter_place) <= 2:
        return
    if pter_place[-1] == pter_place[-2]:
        return
    if pter_place[-1] > 0 >= pter_place[-2]:
        return True
    elif pter_place[-1] <= 0 < pter_place[-2]:
        return False
    else:
        return None


async def send_notify():
    need_to_notify = await need_notify()

    if need_to_notify is None:
        return

    if need_to_notify:
        try:
            text = f"有坑了\n{await commands.pter_place.get_place_message()}"
            await bot.send_message(chat_id=NOTIFY_CHAT, text=text)
            await bot.send_message(chat_id=LOG_CHAT, text=text)
            await bot.send_document(
                WORK_CHAT,
                STICKER_FOR_HAS_PLACE
            )
        except Exception as e:
            await log.error(f"通知时出现了问题\n {e}", "NOTIFY_ERROR")
    elif not need_to_notify:
        try:
            text = f"坑无了\n{await commands.pter_place.get_place_message()}"
            await bot.send_message(chat_id=NOTIFY_CHAT, text=text)
            await bot.send_message(chat_id=LOG_CHAT, text=text)
            await bot.send_document(
                WORK_CHAT,
                STICKER_FOR_NO_PLACE
            )
        except Exception as e:
            await log.error(f"通知时出现了问题\n {e}", "NOTIFY_ERROR")


@Client.on_message(filters.command('notice_me'))
async def notice_me(_, message):
    await reply_and_delay_delete(message, f"请加入通知频道~ \n{NOTIFY_CHAT_INVITE_LINK}", INVITE_LINK_DELETE_TIME)
    # TODO 重写 notice_me，生成邀请链接，私聊发送邀请链接，使用/超出时间限制后销毁。
    # TODO 定时查看用户是否在猫站群组中，如果不在则踢出通知频道。如果是皮套人则在发送私聊链接的时候提醒需要联系我提升为管理员以避免踢出。
