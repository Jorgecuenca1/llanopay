import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llanopay_project.settings')

app = Celery('llanopay')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.task_routes = {
    'apps.crypto.tasks.*': {'queue': 'crypto'},
    'apps.notifications.tasks.*': {'queue': 'notifications'},
}
