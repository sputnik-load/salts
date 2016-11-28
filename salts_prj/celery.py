# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
import os
import json
from celery import Celery
from celery import shared_task
from salts.tankmanager import tank_manager

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "salts_prj.settings")

app = Celery("salts")

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@shared_task
def shoot(tank, scenario, custom_data):
    return tank_manager.shootmq(tank, scenario, custom_data)
