import os

import environ
from celery import Celery
from django.apps import apps
from celery.schedules import crontab
from datetime import datetime


env = environ.Env()
env.read_env(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", env.str("DJANGO_SETTINGS_MODULE", "core.settings"))

app = Celery("saveuz")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
