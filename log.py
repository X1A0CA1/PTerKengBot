import logging

from config import DEFAULT_LOG_LEVEL, LOG_CHAT

from utils import (
    send_message_with_length_check,
    get_fullname_and_user_id_from_message,
    get_chat_tilte_and_id_from_message
)


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


async def _log_user_action(message, log_tag, log_rule, more_log_text=None):
    chat_title, chat_id = await get_chat_tilte_and_id_from_message(message)
    full_name, user_id = await get_fullname_and_user_id_from_message(message)
    if not full_name or not user_id or not chat_title or not chat_id:
        return await _log_messages(
            log_tag="#LOG_USER_ACTION_ERROR",
            log_summaries="日志记录在获取信息时出现了错误",
            log_function=logger.info,
            more_log_text=f"原始消息: {message}"
        )

    log_summaries = (
        f"用户 **{full_name}** ({user_id}) 在群组 **{chat_title}** ({chat_id}) 触发了规则: {log_rule}"
    )
    log_message = (
        f"{log_tag}\n\n"
        f"{log_summaries}"
    )
    if more_log_text:
        log_message += f"\n{more_log_text}"
    await send_message_with_length_check(LOG_CHAT, log_message, log_summaries)
    logger.info(log_message)


async def cmd_eval_log(message, cmd, result):
    more_log_text = f"执行了命令：\n{cmd}\n结果为：\n{result}"
    await _log_user_action(message, "#cmd_eval_log #info", "执行/eval", more_log_text)


async def not_work_group_log(message):
    more_log_text = f"发送的消息为：{message.text}"
    await _log_user_action(message, "#not_work_group_log #info", "非工作群组执行命令", more_log_text)


async def no_permission_log(message):
    more_log_text = f"发送的消息为：{message.text}"
    await _log_user_action(message, "#no_permission_log #info", "无权限执行命令", more_log_text)


async def command_log(message, log_tag, log_rule):
    log_tag += " #command_log"
    await _log_user_action(message, log_tag, log_rule)


async def _log_messages(log_tag, log_summaries, log_function, more_log_text=None):
    log_message = (
        f"{log_tag}\n\n"
        f"{log_summaries}"
    )

    if more_log_text:
        log_message += f"\n{more_log_text}"

    log_function(log_message)
    await send_message_with_length_check(LOG_CHAT, log_message, log_summaries)


async def _need_to_log(log_level):
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.getLevelName(DEFAULT_LOG_LEVEL))
    if log_level >= _logger.level:
        return True
    return False


async def debug(log_tag, log_summaries, more_log_text=None):
    if await _need_to_log(10):
        log_tag += " #debug"
        await _log_messages(
            log_tag=log_tag,
            log_summaries=log_summaries,
            log_function=logger.debug,
            more_log_text=more_log_text
        )


async def info(log_tag, log_summaries, more_log_text=None):
    if await _need_to_log(20):
        log_tag += " #info"
        await _log_messages(
            log_tag=log_tag,
            log_summaries=log_summaries,
            log_function=logger.info,
            more_log_text=more_log_text
        )


async def warning(log_tag, log_summaries, more_log_text=None):
    if await _need_to_log(30):
        log_tag += " #warning"
        await _log_messages(
            log_tag=log_tag,
            log_summaries=log_summaries,
            log_function=logger.warning,
            more_log_text=more_log_text
        )


async def error(log_tag, log_summaries, more_log_text=None):
    if await _need_to_log(40):
        log_tag += " #error"
        await _log_messages(
            log_tag=log_tag,
            log_summaries=log_summaries,
            log_function=logger.error,
            more_log_text=more_log_text
        )


logger = setup_logger()
