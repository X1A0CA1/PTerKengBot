from config import BOT_NAME, BOT_TOKEN, API_ID, API_HASH, LOG_CHAT

from pyrogram import Client, idle
from pyrogram.types import BotCommand

from scheduler import scheduler


bot = Client(
    BOT_NAME,
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="commands")
)


async def start_bot():
    await bot.start()
    scheduler.start()
    await bot.set_bot_commands([
        BotCommand("help", "显示帮助信息"),
        BotCommand("stats", "查看站点统计信息"),
        BotCommand("ping", "小菜只因器人还活着吗？"),
        BotCommand("flush", "强制刷新数据（仅管理可用）"),
        BotCommand("notice_me", "坑位变化通知你"),
        BotCommand("forward_mode", "设置消息转发（仅管理可用）"),
    ])
    print("Bot Started!")
    await bot.send_message(LOG_CHAT, "Bot Started!")
    await idle()




