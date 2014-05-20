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
        'run_segment_0': {
            'task': 'run_segment',
            'schedule': crontab(minute='0,15,30,45'),
            'args': [0]
        },
        'run_segment_1': {
            'task': 'run_segment',
            'schedule': crontab(minute='1,16,31,46'),
            'args': [1]
        },
        'run_segment_2': {
            'task': 'run_segment',
            'schedule': crontab(minute='2,17,32,47'),
            'args': [2]
        },
        'run_segment_3': {
            'task': 'run_segment',
            'schedule': crontab(minute='3,18,33,48'),
            'args': [3]
        },
        'run_segment_4': {
            'task': 'run_segment',
            'schedule': crontab(minute='4,19,34,49'),
            'args': [4]
        },
        'run_segment_5': {
            'task': 'run_segment',
            'schedule': crontab(minute='5,20,35,50'),
            'args': [5]
        },
        'run_segment_6': {
            'task': 'run_segment',
            'schedule': crontab(minute='6,21,36,51'),
            'args': [6]
        },
        'run_segment_7': {
            'task': 'run_segment',
            'schedule': crontab(minute='7,22,37,52'),
            'args': [7]
        },
        'run_segment_8': {
            'task': 'run_segment',
            'schedule': crontab(minute='8,23,38,53'),
            'args': [8]
        },
        'run_segment_9': {
            'task': 'run_segment',
            'schedule': crontab(minute='9,24,39,54'),
            'args': [9]
        },
        'run_segment_10': {
            'task': 'run_segment',
            'schedule': crontab(minute='10,25,40,55'),
            'args': [10]
        },
        'run_segment_11': {
            'task': 'run_segment',
            'schedule': crontab(minute='11,26,41,56'),
            'args': [11]
        },
        'run_segment_12': {
            'task': 'run_segment',
            'schedule': crontab(minute='12,27,42,57'),
            'args': [12]
        },
        'run_segment_13': {
            'task': 'run_segment',
            'schedule': crontab(minute='13,28,43,58'),
            'args': [13]
        },
        'run_segment_14': {
            'task': 'run_segment',
            'schedule': crontab(minute='14,29,44,59'),
            'args': [14]
        },
        'daily_tasks': {
            'task': 'daily_tasks',
            'schedule': crontab(minute='0', hour='0')
        }
    }
)

if __name__ == '__main__':
    app.start()
