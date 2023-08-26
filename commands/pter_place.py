import re
import time
import aiohttp
from bs4 import BeautifulSoup

import log
from scheduler import scheduler
from config import COOKIES, HEADERS
from utils import check_required
from . import notify

from pyrogram import Client, filters

REGISTERED = PENDING = MAX_USERS = UPDATE_TIME = 0

PTER_PLACE = []
MESSAGE_TO_BE_DELETED = []
PTER_DOWN = None

PTER_URL = "https://pterclub.com/index.php"


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
    global REGISTERED, PENDING, MAX_USERS, UPDATE_TIME, PTER_PLACE, PTER_DOWN

    async with aiohttp.ClientSession(headers=HEADERS, cookies=COOKIES) as session:
        raw_html = await _fetch(session, PTER_URL)

        try:
            html = BeautifulSoup(raw_html, 'html.parser')
            status = str(html.find_all('td', class_='rowhead')[2].find_next_sibling('td').text).split("/")
            REGISTERED = int("".join(re.findall(r"\d+", status[0])))
            MAX_USERS = int("".join(re.findall(r"\d+", status[1])))
            PENDING = int(str(html.find_all('td', class_='rowhead')[4].find_next_sibling('td').text))
            UPDATE_TIME = time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time()))
            PTER_PLACE.append(MAX_USERS - REGISTERED - PENDING)

            if PTER_DOWN:
                PTER_DOWN = False
                await log.info(
                    log_tag="#PTER_BACK",
                    log_summaries="猫站已恢复"
                )
            elif PTER_DOWN is None:
                PTER_DOWN = False

            await log.debug(
                log_tag="#PTER_PLACE",
                log_summaries=f"获取到了新的坑位信息：\n\n{await get_place_message()}"
            )

            return
        except Exception as e:
            if not PTER_DOWN:
                PTER_DOWN = True
            await log.warning(
                log_tag="#PTER_DOWN",
                log_summaries="猫站可能挂了。解析html时出现了错误:",
                more_log_text=f"{e}\n\n raw_html: \n{raw_html}"
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


@Client.on_message(filters.command('stats'))
async def status_message(_, message):
    if await check_required(message, work_group_required=True):
        await _send_status_message(message)
        await log.command_log(message, "#RAN_COMMAND_STATS", "执行/stats")


@Client.on_message(filters.command('flush'))
async def flush_message(_, message):
    if await check_required(message, admin_required=True):
        await get_pter_place_and_notify()
        await _send_status_message(message)
        await log.command_log(message, "#RAN_COMMAND_FLUSH",
                              f"执行/flush，返回为：\n获取到了新的坑位信息：\n\n{await get_place_message()}")
