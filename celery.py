from __future__ import absolute_import

from celery import Celery

app = Celery('WikiApiary',
             broker='redis://',
             backend='redis://',
             include=['WikiApiary.tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
    CELERY_ACCEPT_CONTENT = ['pickle', 'json']
)

if __name__ == '__main__':
    app.start()