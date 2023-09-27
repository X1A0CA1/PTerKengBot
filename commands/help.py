from pyrogram import Client, filters

import log
from config import BOT_NAME, HELP_DELETE_TIME
from utils import reply_and_delay_delete

HELP_MESSAGE = f"""
**PTerKengBot HELP**
```
/help@{BOT_NAME}               显示此帮助信息
/ping@{BOT_NAME}               查看机器人存活状态
/stats@{BOT_NAME}           *  查看站点统计信息
/keng@{BOT_NAME}            *  等价于 stats
/notice_me@{BOT_NAME}       *  获取坑位通知频道链接
/flush@{BOT_NAME}           !  强制刷新数据
/eval@{BOT_NAME}            !  ~~调教 bot 使用的命令~~

/forward_mode on/off       !P  自动转发接下来私聊 BOT 的消息到猫站群
    /edit <msg_link> <text>    !P  编辑指定消息
    /delete <msg_link>         !P  删除指定消息
    /reply <msg_link>          !P  回复指定消息 
```
        
带有 ! 的命令仅管理员(被认证的机器人管理员、非匿名群组管理员）可用，皮套人仅可在群组内使用，无法在私聊使用；
带有 * 的命令仅可以在猫站群内使用。
带有 P 的命令仅可以在私聊内使用。

**机器人带有黑名单、日志收集，请勿滥用** 。\n@PterKengBot 不是官方所编写、维护的的机器人。
v1.4.3@PlanTech"
"""


@Client.on_message(filters.command('help'), group=0)
async def help_message(_, message):
    await reply_and_delay_delete(message, HELP_MESSAGE, HELP_DELETE_TIME)
    await log.command_log(message, "#RAN_COMMAND_HELP", "执行/help")
