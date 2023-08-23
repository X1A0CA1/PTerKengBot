import sys
import io
import traceback

from pyrogram import Client, filters

import log
from utils import delay_delete, reply_and_delay_delete, check_permission, reply_message_with_length_check


async def run_eval(cmd: str, message=None, only_result: bool = False) -> str:
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(cmd, message, Client)
    except Exception:  # noqa
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"
    return evaluation if only_result else f"**>>>** `{cmd}` \n`{evaluation}`"


async def aexec(code, event, client):
    exec(
        (
                (
                        ("async def __aexec(e, client): " + "\n msg = message = e")
                        + "\n reply = message.reply_to_message if message else None"
                )
                + "\n chat = e.chat if e else None"
        )
        + "".join(f"\n {x}" for x in code.split("\n"))
    )

    return await locals()["__aexec"](event, client)


@Client.on_message(filters.command("eval"))
async def python_eval(_, message):
    if not await check_permission(message):
        return await reply_and_delay_delete(message, "你没有权限使用该命令", 3)
    try:
        cmd = message.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return
    final_output = await run_eval(cmd, message)
    await delay_delete(
        await reply_message_with_length_check(message, final_output),
        30
    )
    return await log.cmd_eval_log(message, cmd, final_output)
