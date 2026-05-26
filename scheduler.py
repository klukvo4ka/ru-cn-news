import logging
from apscheduler.schedulers.background import BackgroundScheduler
from models import init_db, save_articles
from parser import fetch_articles as _fetch

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

_scheduler = BackgroundScheduler(timezone="UTC")


def fetch_and_store():
    try:
        articles = _fetch()
        saved = save_articles(articles)
        log.info("fetched=%d saved=%d", len(articles), saved)
    except Exception as e:
        log.error("fetch failed: %s", e)


def start_scheduler():
    if _scheduler.running:
        return
    _scheduler.add_job(fetch_and_store, "interval", minutes=30, id="news_fetch")
    _scheduler.start()
    log.info("scheduler started, interval=30m")
