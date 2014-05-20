"""
Module to kick off celery beat scheduled tasks.
Celery cannot invoke object methods directly, so these tasks
take care of that.
"""

from WikiApiary.apiary.tasks.bot.deletebotlogs import DeleteBotLogsTask
from WikiApiary.apiary.tasks.bot.deletewebsitelogs import DeleteWebsiteLogsTask
from WikiApiary.apiary.tasks.bot.updatetagline import UpdateTaglineTask
from WikiApiary.apiary.tasks.bot.updatetotaledits import UpdateTotalEditsTask
from WikiApiary.apiary.tasks.bot.websitesegment import ProcessWebsiteSegment
from WikiApiary.celery import app
import logging


LOGGER = logging.getLogger()

@app.task(name='run_segment')
def run_segment(segment_id):
    """Invoke and run the website segment."""
    LOGGER.info("Running segment %d" % segment_id)
    task = ProcessWebsiteSegment()
    task.run(segment_id)

@app.task(name='daily_tasks')
def run_daily_tasks():
    """Run daily tasks."""
    LOGGER.info("Running daily tasks.")

    task = DeleteBotLogsTask()
    task.run()

    task = DeleteWebsiteLogsTask()
    task.run()

    task = UpdateTaglineTask()
    task.run()

    task = UpdateTotalEditsTask()
    task.run()
