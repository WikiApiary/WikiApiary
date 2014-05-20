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
        'WikiApiary.apiary.tasks.bot.deletebotlogs',
        'WikiApiary.apiary.tasks.bot.deletewebsitelogs',
        'WikiApiary.apiary.tasks.bot.updatetagline',
        'WikiApiary.apiary.tasks.bot.updatetotaledits',
        'WikiApiary.apiary.tasks.bot.websitesegment',
        'WikiApiary.apiary.tasks.website.extensions',
        'WikiApiary.apiary.tasks.website.general',
        'WikiApiary.apiary.tasks.website.interwikimap',
        'WikiApiary.apiary.tasks.website.maxmind',
        'WikiApiary.apiary.tasks.website.namespaces',
        'WikiApiary.apiary.tasks.website.skins',
        'WikiApiary.apiary.tasks.website.smwinfo',
        'WikiApiary.apiary.tasks.website.statistics',
        'WikiApiary.apiary.tasks.website.whoislookup',
        'WikiApiary.apiary.tasks.scheduled'
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
