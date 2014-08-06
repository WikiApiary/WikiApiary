"""
Module to kick off celery beat scheduled tasks.
Celery cannot invoke object methods directly, so these tasks
take care of that.
"""

from apiary.tasks.bot.audit_websites import AuditWebsites
from apiary.tasks.bot.deletebotlogs import DeleteBotLogsTask
from apiary.tasks.bot.deletewebsitelogs import DeleteWebsiteLogsTask
from apiary.tasks.bot.extension_weekly import ExtensionWeekly
from apiary.tasks.bot.updatetagline import UpdateTaglineTask
from apiary.tasks.bot.updatetotaledits import UpdateTotalEditsTask
from apiary.tasks.bot.websitesegment import ProcessWebsiteSegment
from apiary.tasks.bot.notify_segment import NotifySegment
from apiary.celery import app
import logging
import datetime


LOGGER = logging.getLogger()

@app.task(name='run_segment')
def run_segment(segment_id = None):
    """Invoke and run the website segment."""

    # If segment_id isn't provided calculate what it should be
    if segment_id is None:
        segment_id = int(datetime.datetime.now().strftime("%M")) % 15

    LOGGER.info("Running segment %d", segment_id)
    task = ProcessWebsiteSegment()
    task.run(segment_id)

@app.task(name='audit_websites')
def run_audit_websites():
    """Invoke and run the audit website tasks."""
    LOGGER.info("Running audit websites task.")

    task = AuditWebsites()
    task.run()

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

@app.task(name='notify_segment')
def run_notify_segment():
    """Send notifications each hour."""
    LOGGER.info("Starting notifications")

    task = NotifySegment()
    task.run()

@app.task(name='extension_weekly')
def run_extension_weekly():
    """Kick off weekly extesnion jobs."""
    LOGGER.info("Starting extension weekly")

    task = ExtensionWeekly()
    task.run
