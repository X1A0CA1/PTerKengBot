from pyrogram import Client, filters

from config import BOT_NAME, HELP_DELETE_TIME
from utils import reply_and_delay_delete


HELP_MESSAGE = (
    f"**PTerKengBot HELP**\n"
    f"`/help@{BOT_NAME}`    显示此帮助信息\n"
    f"`/stats@{BOT_NAME}`    `*` 查看站点统计信息\n"
    f"`/ping@{BOT_NAME}`    查看机器人存活状态\n"
    f"`/flush@{BOT_NAME}`    `!` 强制刷新数据\n"
    f"`/notice_me@{BOT_NAME}`    `*` 当坑位变化的时候私信通知你\n"
    f"`/cancel_notice@{BOT_NAME}`    取消通知\n"
    f"`/eval@{BOT_NAME}`    `!` 奇怪的东西\n\n"
    f"带有 `!` 的命令仅管理员(被认证的机器人管理员、带有角标的群组管理员、皮套人)可用；带有 `*` 的命令仅可以在猫站群内使用。\n\n"
    f"**机器人带有黑名单、日志收集，请勿滥用**。\n@PterKengBot 不是官方所编写的的机器人。\n\n"
    f"v1.2.1@PlanTech"
)


@Client.on_message(filters.command('help'))
async def help_message(_, message):
    return await reply_and_delay_delete(message, HELP_MESSAGE, HELP_DELETE_TIME)
