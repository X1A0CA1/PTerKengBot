import asyncio
from PterKengBot import start_bot

loop = asyncio.get_event_loop()
loop.run_until_complete(start_bot())
