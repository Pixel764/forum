import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('forum')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.timezone = settings.TIME_ZONE

app.conf.beat_schedule = {
    'delete_expired_email_codes': {
        'task': 'users.tasks.delete_expired_email_codes',
        'schedule': 60.0,
    }
}
