"""
Base celery app definition.
"""
# pylint: disable=C0103

from __future__ import absolute_import
from celery import Celery

app = Celery(
    'WikiApiary',
    broker='redis://',
    backend='redis://',
    include=[
        'WikiApiary.apiary.tasks.website.extensions',
        'WikiApiary.apiary.tasks.website.general',
        'WikiApiary.apiary.tasks.website.maxmind',
        'WikiApiary.apiary.tasks.website.skins',
        'WikiApiary.apiary.tasks.website.smwinfo',
        'WikiApiary.apiary.tasks.website.statistics',
        'WikiApiary.apiary.tasks.website.whoislookup' 
    ]
)

# Optional configuration, see the application user guide.
app.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
    CELERY_ACCEPT_CONTENT = ['pickle', 'json']
)

if __name__ == '__main__':
    app.start()
