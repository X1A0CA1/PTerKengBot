import json

import commands.pter_place
from config import LOG_CHAT, WORK_CHAT, INFO_DELETE_TIME
from PterKengBot import bot
from utils import reply_and_delay_delete, check_work_group

from pyrogram import Client, filters


try:
    with open("notification_list.json", "r") as fl:
        NOTIFICATION_LIST = json.load(fl)
except FileNotFoundError:
    NOTIFICATION_LIST = []


async def add_to_notification_list(user_id):
    global NOTIFICATION_LIST
    NOTIFICATION_LIST.append(user_id)
    with open("notification_list.json", "w") as fl:
        json.dump(NOTIFICATION_LIST, fl)


async def remove_from_notification_list(user_id):
    global NOTIFICATION_LIST
    NOTIFICATION_LIST.remove(user_id)
    with open("notification_list.json", "w") as fl:
        json.dump(NOTIFICATION_LIST, fl)


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


async def chat_notify():
    need_to_notify = await need_notify()
    if need_to_notify is None:
        return

    if need_to_notify:
        try:
            await bot.send_message(chat_id=LOG_CHAT, text="有坑了")
            await bot.send_document(
                WORK_CHAT,
                "BQACAgUAAx0ETaitjQABDrVbZC7-CyRnP9bNWyL6uyQTsEZYmhUAAgIIAAKBgXlVI9gBrugVVmAeBA"
            )
        except Exception as e:
            print(f"无法通知 {WORK_CHAT},\n {e}")
    elif not need_to_notify:
        try:
            await bot.send_message(chat_id=LOG_CHAT, text="坑无了")
            await bot.send_document(
                WORK_CHAT,
                "BQACAgUAAx0ETaitjQABDrVcZC7-DHoDQxTig8mGKF4tXTtDjZUAAgMIAAKBgXlVIUkm6W3k8YseBA"
            )
        except Exception as e:
            print(f"无法通知 {WORK_CHAT},\n {e}")


async def pm_notify():
    need_to_notify = await need_notify()
    if need_to_notify is None:
        return
    if len(NOTIFICATION_LIST) == 0:
        return
    for user_id in NOTIFICATION_LIST:
        try:
            await bot.send_message(user_id, "有坑了" if need_to_notify else "坑无了")
        except Exception as e:
            await bot.send_message(LOG_CHAT, f"无法通知 {user_id},\n {e}")


@Client.on_message(filters.command('notice_me'))
async def notice_me(_, message):
    if not await check_work_group(message):
        return await reply_and_delay_delete(message, "请在猫站群内使用该命令", INFO_DELETE_TIME)

    if message.sender_chat:
        return await reply_and_delay_delete(message, "皮套爬！", INFO_DELETE_TIME)

    global NOTIFICATION_LIST
    if message.from_user.id in NOTIFICATION_LIST:
        return await reply_and_delay_delete(message, "你已经开启过通知了", INFO_DELETE_TIME)
    else:
        try:
            await bot.send_message(message.from_user.id, "已开启私聊通知")
            await reply_and_delay_delete(message, "已开启私聊通知", INFO_DELETE_TIME)
            await add_to_notification_list(message.from_user.id)
        except Exception as e:
            print(f"无法私聊 {message.from_user.id},\n {e}")
            return await reply_and_delay_delete(message, "请先私聊我一次，我才能够私聊你通知", INFO_DELETE_TIME)


@Client.on_message(filters.command('cancel_notice'))
async def cancel_notice(_, message):
    if message.sender_chat:
        return await reply_and_delay_delete(message, "皮套爬！", INFO_DELETE_TIME)

    global NOTIFICATION_LIST
    if message.from_user.id not in NOTIFICATION_LIST:
        return await reply_and_delay_delete(message, "你还没有开启通知", INFO_DELETE_TIME)
    else:
        await bot.send_message(message.from_user.id, "已关闭私聊通知")
        await reply_and_delay_delete(message, "已关闭私聊通知", INFO_DELETE_TIME)
        await remove_from_notification_list(message.from_user.id)
