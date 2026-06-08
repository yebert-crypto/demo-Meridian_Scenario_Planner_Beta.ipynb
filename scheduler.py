"""
Background scheduler — runs scans on a fixed interval.
Run independently of the Streamlit app:  python scheduler.py

Alternatively, deploy as a cron job or cloud function.
"""
import logging
import time

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from meridian.scanner import run_scan

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

scheduler = BlockingScheduler()


@scheduler.scheduled_job(CronTrigger(hour="7,12,17", minute="0"))  # 7am, noon, 5pm
def scheduled_scan():
    log.info("Starting scheduled scan…")
    result = run_scan(lookback_days=1)
    log.info("Scan complete: %s", result)


if __name__ == "__main__":
    log.info("Meridian scheduler starting. Scans run at 7am, 12pm, 5pm UTC.")
    try:
        scheduler.start()
    except KeyboardInterrupt:
        log.info("Scheduler stopped.")
