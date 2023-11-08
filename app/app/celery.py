from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

app = Celery('app')

app.conf.timezone = settings.TIME_ZONE
app.config_from_object('django.conf:settings', namespace='CELERY')


app.autodiscover_tasks()
app.conf.beat_schedule = {
    'increase_debt_every_3_hours': {
        'task': 'core.tasks.increase_debt',
        'schedule': crontab(hour='*/3'),
    },
    'decrease_debt_at_6_30': {
        'task': 'core.tasks.decrease_debt',
        'schedule': crontab(hour=6, minute=30),
    },
}

