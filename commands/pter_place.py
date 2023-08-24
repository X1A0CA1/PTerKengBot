import re
import time
import aiohttp
from bs4 import BeautifulSoup

import log
from scheduler import scheduler
from config import COOKIES, HEADERS, INFO_DELETE_TIME
from utils import reply_and_delay_delete, check_permission, check_work_group
from . import notify

from pyrogram import Client, filters

REGISTERED = PENDING = MAX_USERS = UPDATE_TIME = 0

PTER_PLACE = []
MESSAGE_TO_BE_DELETED = []


async def _clean_pter_place():
    global PTER_PLACE
    if len(PTER_PLACE) > 20:
        PTER_PLACE = PTER_PLACE[-20:]


async def _fetch(session, url):
    async with session.get(url) as response:
        if response.status != 200:
            return None
        return await response.text()


async def _get_pter_status():
    async with aiohttp.ClientSession(headers=HEADERS, cookies=COOKIES) as session:
        raw_html = await _fetch(session, f'https://pterclub.com/index.php')
        if raw_html is None:
            return
        try:
            html = BeautifulSoup(raw_html, 'html.parser')
        except Exception as e:
            await log.warning(
                log_tag="#HTML_PARSE_ERROR",
                log_summaries="bs解析html时出现了错误:",
                more_log_text=f"{e}\n\n raw_html: \n{raw_html}"
            )
            return

        global REGISTERED, PENDING, MAX_USERS, UPDATE_TIME, PTER_PLACE
        try:
            status = str(html.find_all('td', class_='rowhead')[2].find_next_sibling('td').text).split("/")
            REGISTERED = int("".join(re.findall(r"\d+", status[0])))
            MAX_USERS = int("".join(re.findall(r"\d+", status[1])))
            PENDING = int(str(html.find_all('td', class_='rowhead')[4].find_next_sibling('td').text))
        except Exception as e:
            await log.warning(
                log_tag="#HTML_PARSE_ERROR",
                log_summaries="在html中获取信息出现了错误:",
                more_log_text=f"{e}\n\n raw_html: \n{raw_html}"
            )
            return
        UPDATE_TIME = time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time()))

        PTER_PLACE.append(MAX_USERS - REGISTERED - PENDING)
        await log.debug(
            log_tag="#PTER_PLACE",
            log_summaries=f"获取到了新的坑位信息：\n\n{await get_place_message()}"
        )
        return


@scheduler.scheduled_job("interval", seconds=30)
async def get_pter_place_and_notify():
    await _get_pter_status()
    await notify.send_notify()


@scheduler.scheduled_job("interval", seconds=3600)
async def clean_pter_place_job():
    await _clean_pter_place()


# 组装消息
async def get_place_message():
    global REGISTERED, PENDING, MAX_USERS, UPDATE_TIME
    free = MAX_USERS - REGISTERED - PENDING
    if free < 0:
        info = f"当前坑位溢出 {abs(free)} 人"
    elif free == 0:
        info = "当前猫站不多不少刚好满～"
    else:
        info = f"当前剩余坑位 {free} 人"
    return (
        f"当前坑位: {REGISTERED + PENDING} (含 {PENDING} 待注册) / {MAX_USERS}\n\n"
        f"{info}\n\n"
        f"数据更新时间: {UPDATE_TIME}"
    )


async def _delete_status_message():
    global MESSAGE_TO_BE_DELETED
    for message in MESSAGE_TO_BE_DELETED:
        try:
            await message.delete()
        except Exception as e:
            MESSAGE_TO_BE_DELETED = []
            await log.warning(
                log_tag="#DELETE_STATUS_MESSAGE_ERROR",
                log_summaries="在删除以前的/stats回复消息时虽然出现了错误，但已清空列表:",
                more_log_text=f"{e}"
            )


async def _send_status_message(message):
    message = await message.reply(await get_place_message())
    await _delete_status_message()
    MESSAGE_TO_BE_DELETED.append(message)


async def _check_and_reply(message, permission_required=False, work_group_required=False):
    if work_group_required and not await check_work_group(message):
        await log.not_work_group_log(message)
        return await reply_and_delay_delete(message, "请在猫站群内使用该命令", INFO_DELETE_TIME)

    if permission_required and not await check_permission(message):
        await log.no_permission_log(message)
        return await reply_and_delay_delete(message, "你没有权限使用该命令", INFO_DELETE_TIME)

    return True


@Client.on_message(filters.command('stats'))
async def status_message(_, message):
    if await _check_and_reply(message, work_group_required=True):
        await _send_status_message(message)
        await log.command_log(message, "#RAN_COMMAND_STATS", "执行/stats")


@Client.on_message(filters.command('flush'))
async def flush_message(_, message):
    if await _check_and_reply(message, permission_required=True):
        await get_pter_place_and_notify()
        await _send_status_message(message)
        await log.command_log(message, "#RAN_COMMAND_FLUSH", "执行了/flush")
