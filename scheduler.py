from apscheduler.schedulers.background import BackgroundScheduler

import downloader

# Use a singleton scheduler instance
_scheduler = None

def get_scheduler():
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler()
        _scheduler.start()
    return _scheduler

def schedule_download(url: str, method: str, run_datetime):
    """
    Schedule a one-time download job at the given datetime.
    """
    scheduler = get_scheduler()
    job = scheduler.add_job(
        downloader.download_video, 
        'date', 
        run_date=run_datetime,
        args=[url, method]
    )
    return job
