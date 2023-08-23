import sys
import io
import traceback

from pyrogram import Client, filters

from config import LOG_CHAT
from utils import reply_and_delay_delete, check_permission


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
async def python_eval(client, message):
    if not await check_permission(message):
        return await reply_and_delay_delete(message, "你没有权限使用该命令", 3)
    try:
        cmd = message.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return
    final_output = await run_eval(cmd, message)
    ran_command_user = str(message.from_user.id) if message.from_user else ''
    ran_command_user += str(message.sender_chat.id) if message.sender_chat else ''
    log_message = f"User {ran_command_user} ran eval command:\n`{cmd}`\nThe result is:\n{final_output}"
    print(log_message)
    await client.send_message(LOG_CHAT, log_message)
    await reply_and_delay_delete(message, final_output, 10)
