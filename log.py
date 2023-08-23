import logging
from config import DEFAULT_LOG_LEVEL, LOG_CHAT

from PterKengBot import bot
from utils import get_user_fullname_from_message, get_chat_fullname_from_message, send_message_with_length_check


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


async def _log_command_execution(message, log_type, cmd, result):
    if message.from_user:
        full_name = await get_user_fullname_from_message(message)
        user_id = message.from_user.id
    elif message.sender_chat:
        full_name = await get_chat_fullname_from_message(message)
        user_id = message.sender_chat.id
    else:
        return logger.error(
            f"在记录日志时，无法获取用户信息，原始消息：\n{message}\n命令为：\n{cmd}\n响应为:\n{result}",
            message, cmd, result
        )

    log_message_summaries = f"用户 **{full_name}**；(`{user_id}`) 执行了命令：\n"
    log_message = (
        f"#{log_type}\n\n"
        f"{log_message_summaries}"
        f"`{cmd}`\n\n"
        f"结果为：\n"
        f"{result}"
    )
    await send_message_with_length_check(LOG_CHAT, log_message, log_type, log_message_summaries)
    logger.info(log_message)


async def _log_user_action(message, log_type, log_message_prefix):
    if message.from_user:
        full_name = await get_user_fullname_from_message(message)
        user_id = message.from_user.id
    elif message.sender_chat:
        full_name = await get_chat_fullname_from_message(message)
        user_id = message.sender_chat.id
    else:
        return logger.error(
            f"用户 {log_message_prefix}。但无法获取用户信息，原始消息：\n{message}\n",
            message
        )
    log_message_summaries = f"用户 **{full_name}**；(`{user_id}`) {log_message_prefix}：\n"
    log_message = (
        f"#{log_type}\n\n"
        f"{log_message_summaries}"
        f"{message.text}"
    )

    await send_message_with_length_check(LOG_CHAT, log_message, log_type, log_message_summaries)
    logger.info(log_message)


async def _log_messages(log_type, log_message_content, log_function):
    log_message = (
        f"#{log_type}\n\n"
        f"{log_message_content}"
    )
    log_function(log_message)
    await send_message_with_length_check(LOG_CHAT, log_message, log_type)


async def cmd_eval_log(message, cmd, result):
    await _log_command_execution(message, "cmd_eval_log", cmd, result)


async def not_work_group_log(message):
    await _log_user_action(message, "not_work_group_log", "在非工作群组执行了命令")


async def no_permission_log(message):
    await _log_user_action(message, "no_permission_log", "没有权限执行命令")


async def command_log(message, log_type, log_message_prefix):
    await _log_user_action(message, log_type, log_message_prefix)


async def _need_to_log(log_level):
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.getLevelName(DEFAULT_LOG_LEVEL))
    if log_level >= _logger.level:
        return True
    return False


async def debug(debug_message, log_type="debug"):
    if await _need_to_log(10):
        await _log_messages(log_type, debug_message, logger.debug)


async def info(info_message, log_type="info"):
    if await _need_to_log(20):
        await _log_messages(log_type, info_message, logger.info)


async def warning(warning_message, log_type="warning"):
    if await _need_to_log(30):
        await _log_messages(log_type, warning_message, logger.warning)


async def error(error_message, log_type="error"):
    if await _need_to_log(40):
        await _log_messages(log_type, error_message, logger.error)


logger = setup_logger()
