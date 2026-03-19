"""
scheduler.py — Run the MLB trending players job on a cron schedule.

Default: Every Wednesday and Sunday at 7:00 PM (local time).
Configure via SCHEDULE_DAYS, SCHEDULE_HOUR, SCHEDULE_MINUTE in .env
"""
import logging
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from scraper import scrape_trending_players
from emailer import send_email
import config

logger = logging.getLogger(__name__)


def job() -> None:
    """Fetch trending players and send the email digest."""
    logger.info("[%s] Running scheduled MLB trending players job…", datetime.now().isoformat())
    try:
        players = scrape_trending_players()
        if not players:
            logger.warning("No trending players scraped — email not sent.")
            return
        send_email(players)
        logger.info("Job complete. %d players included in email.", len(players))
    except Exception as exc:  # noqa: BLE001
        logger.exception("Job failed: %s", exc)


def start_scheduler() -> None:
    """Start the blocking APScheduler with the configured cron trigger."""
    scheduler = BlockingScheduler()

    trigger = CronTrigger(
        day_of_week=config.SCHEDULE_DAYS,   # e.g. "wed,sun"
        hour=config.SCHEDULE_HOUR,           # 19
        minute=config.SCHEDULE_MINUTE,       # 0
    )

    scheduler.add_job(job, trigger, name="mlb_trending_emailer")

    days_display = config.SCHEDULE_DAYS.replace(",", ", ").title()
    logger.info(
        "Scheduler started. Will run every %s at %02d:%02d. Press Ctrl+C to stop.",
        days_display,
        config.SCHEDULE_HOUR,
        config.SCHEDULE_MINUTE,
    )

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")
