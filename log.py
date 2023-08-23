import logging
from config import DEFAULT_LOG_LEVEL, LOG_CHAT

from PterKengBot import bot
from utils import get_user_fullname_from_message, get_chat_fullname_from_message


def setup_logger():
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.getLevelName(DEFAULT_LOG_LEVEL))

    # 控制台
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.getLevelName(DEFAULT_LOG_LEVEL))

    # 格式化
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    _logger.addHandler(console_handler)
    return _logger


async def cmd_eval_log(message, cmd, result):
    if message.from_user:
        full_name = await get_user_fullname_from_message(message)
        user_id = message.from_user.id
    elif message.sender_chat:
        full_name = await get_chat_fullname_from_message(message)
        user_id = message.sender_chat.id
    else:
        return logger.error(
            "在记录日志时，无法获取用户信息，原始消息：\n%s\n命令为：\n%s\n响应为:\n%s",
            message, cmd, result
        )

    log_message = (
        f"用户 **{full_name}**；(`{user_id}`) 执行了命令：\n"
        f"`{cmd}`\n"
        f"结果为：\n"
        f"{result}"
    )
    await bot.send_message(LOG_CHAT, log_message, disable_web_page_preview=True)
    logger.info(log_message)
    return


logger = setup_logger()
