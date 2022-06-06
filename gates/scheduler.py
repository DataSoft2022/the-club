from apscheduler.schedulers.background import BackgroundScheduler
from .zk_api import get_history, play_with

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(get_history, 'interval', seconds=5)
    scheduler.add_job(play_with, 'interval', seconds=6)
    scheduler.start()
