from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import register_events, DjangoJobStore
from .views import update_rental_info
import logging

logger = logging.getLogger(__name__)

def start():
    scheduler=BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), 'djangojobstore')
    
    register_events(scheduler)

    @scheduler.scheduled_job('cron', hour=0, minute=0, name = 'update_rental_info')
    def auto_check():
        update_rental_info()

    scheduler.start()
    logger.info("Scheduler started!")
