"""
Module to kick off celery beat scheduled tasks.
Celery cannot invoke object methods directly, so these tasks
take care of that.
"""

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
