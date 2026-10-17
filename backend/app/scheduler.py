import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from .database import SessionLocal
from .notifikacije import proveri_podsetnike

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def dnevna_provera():
    """Pokreće se svaki dan u 9:00."""
    logger.info("Pokrećem dnevnu proveru podsetnika...")
    db = SessionLocal()
    try:
        proveri_podsetnike(db)
    finally:
        db.close()


def start_scheduler():
    """Pokreće scheduler."""
    scheduler.add_job(
        dnevna_provera,
        CronTrigger(hour=9, minute=0),
        id="dnevna_provera",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler pokrenut — provera svaki dan u 9:00")