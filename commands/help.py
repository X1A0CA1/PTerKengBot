from pyrogram import Client, filters

import log
from config import BOT_NAME, HELP_DELETE_TIME
from utils import reply_and_delay_delete


HELP_MESSAGE = (
    f"**PTerKengBot HELP**\n\n"
    f"`/help@{BOT_NAME}`    显示此帮助信息\n"
    f"`/stats@{BOT_NAME}`    `*` 查看站点统计信息\n"
    f"`/ping@{BOT_NAME}`    查看机器人存活状态\n"
    f"`/flush@{BOT_NAME}`    `!` 强制刷新数据\n"
    f"`/notice_me@{BOT_NAME}`    `*` 获取坑位通知频道链接\n"
    f"`/eval@{BOT_NAME}`    `!` 奇怪的东西\n\n"
    f"带有 `!` 的命令仅管理员(被认证的机器人管理员、非匿名群组管理员）可用，皮套人仅可在群组内使用，无法在私聊使用；带有 `*` 的命令仅可以在猫站群内使用。\n\n"
    f"**机器人带有黑名单、日志收集，请勿滥用**。\n@PterKengBot 不是官方所编写、维护的的机器人。\n\n"
    f"v1.3.6@PlanTech"
)


@Client.on_message(filters.command('help'))
async def help_message(_, message):
    await reply_and_delay_delete(message, HELP_MESSAGE, HELP_DELETE_TIME)
    await log.command_log(message, "#RAN_COMMAND_HELP", "执行/help")
