from __future__ import absolute_import, unicode_literals

import os

from celery import Celery, shared_task

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

app = Celery("proj")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))


@shared_task(max_retires=3, soft_time_limit=60)
def add(x, y):
    a = x + y
    return a


# Detect whether Celery is available and running
def get_celery_worker_status():
    try:
        insp = app.control.inspect()
        nodes = insp.stats()
        if not nodes:
            return "error: celery is not running"
        return "working"
    except Exception as e:
        return "error: celery is not running"
