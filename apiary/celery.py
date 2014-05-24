"""
Base celery app definition.
"""
# pylint: disable=C0103

from __future__ import absolute_import
from celery import Celery
from celery.schedules import crontab
from datetime import timedelta


app = Celery(
    'WikiApiary',
    broker='redis://',
    backend='redis://',
    include=[
        'apiary.tasks.bot.deletebotlogs',
        'apiary.tasks.bot.deletewebsitelogs',
        'apiary.tasks.bot.updatetagline',
        'apiary.tasks.bot.updatetotaledits',
        'apiary.tasks.bot.websitesegment',
        'apiary.tasks.website.extensions',
        'apiary.tasks.website.general',
        'apiary.tasks.website.interwikimap',
        'apiary.tasks.website.maxmind',
        'apiary.tasks.website.namespaces',
        'apiary.tasks.website.skins',
        'apiary.tasks.website.smwinfo',
        'apiary.tasks.website.statistics',
        'apiary.tasks.website.whoislookup',
        'apiary.tasks.scheduled'
    ]
)

# Optional configuration, see the application user guide.
app.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
    CELERY_ACCEPT_CONTENT = ['pickle', 'json'],
    CELERYBEAT_SCHEDULE = {
        'run_segment': {
            'task': 'run_segment',
            'schedule': crontab()
        },
        'daily_tasks': {
            'task': 'daily_tasks',
            'schedule': crontab(minute='0', hour='0')
        }
    }
)

if __name__ == '__main__':
    app.start()
