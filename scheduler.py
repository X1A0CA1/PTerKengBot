from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler

from config import TIME_ZONE

scheduler = AsyncIOScheduler(scheduler=BackgroundScheduler(timezone=TIME_ZONE))
