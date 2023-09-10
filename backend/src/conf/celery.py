import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")

app = Celery("conf")

app.config_from_object("conf.celery_settings", namespace="CELERY")

app.autodiscover_tasks()
