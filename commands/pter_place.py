import re
import time
import aiohttp
from bs4 import BeautifulSoup

from scheduler import scheduler
from config import COOKIES, HEADERS, INFO_DELETE_TIME, STATS_DELETE_TIME
from utils import reply_and_delay_delete, check_permission, check_work_group
from . import notify

from pyrogram import Client, filters

REGISTERED = PENDING = MAX_USERS = UPDATE_TIME = 0

PTER_PLACE = []


async def clean_pter_place():
    global PTER_PLACE
    if len(PTER_PLACE) > 20:
        PTER_PLACE = PTER_PLACE[-20:]
    return


async def fetch(session, url):
    async with session.get(url) as response:
        if response.status != 200:
            return None
        return await response.text()


async def get_pter_status():
    async with aiohttp.ClientSession(headers=HEADERS, cookies=COOKIES) as session:
        raw_html = await fetch(session, f'https://pterclub.com/index.php')
        if raw_html is None:
            return
        try:
            html = BeautifulSoup(raw_html, 'html.parser')
        except Exception as e:
            print(e)
            return

        global REGISTERED, PENDING, MAX_USERS, UPDATE_TIME, PTER_PLACE
        status = str(html.find_all('td', class_='rowhead')[2].find_next_sibling('td').text).split("/")
        REGISTERED = int("".join(re.findall(r"\d+", status[0])))
        MAX_USERS = int("".join(re.findall(r"\d+", status[1])))
        PENDING = int(str(html.find_all('td', class_='rowhead')[4].find_next_sibling('td').text))
        UPDATE_TIME = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

        PTER_PLACE.append(MAX_USERS - REGISTERED - PENDING)
        return


@scheduler.scheduled_job("interval", seconds=3000)  # TODO 这里到生产环境改为 30
async def main():
    await get_pter_status()
    await notify.chat_notify()
    await notify.pm_notify()
    await clean_pter_place()


async def send_status_message(message):
    global REGISTERED, PENDING, MAX_USERS, UPDATE_TIME
    free = MAX_USERS - REGISTERED - PENDING
    if free < 0:
        info = f"当前坑位溢出 {abs(free)} 人"
    elif free == 0:
        info = "当前猫站不多不少刚好满～"
    else:
        info = f"当前剩余坑位 {free} 人"

    await reply_and_delay_delete(
        message,
        f"当前坑位: {REGISTERED} (已注册) + {PENDING} (待注册) / {MAX_USERS} (最大用户数)\n"
        f"{info}\n"
        f"数据更新时间: {UPDATE_TIME}",
        STATS_DELETE_TIME
    )


@Client.on_message(filters.command('stats'))
async def status_message(_, message):
    if not await check_work_group(message):
        return await reply_and_delay_delete(message, "请在猫站群内使用该命令", INFO_DELETE_TIME)
    await send_status_message(message)


@Client.on_message(filters.command('flush'))
async def flush_message(_, message):
    if not await check_permission(message):
        return await reply_and_delay_delete(message, "你没有权限使用该命令", INFO_DELETE_TIME)
    await get_pter_status()
    await notify.chat_notify()
    await notify.pm_notify()
    await send_status_message(message)
