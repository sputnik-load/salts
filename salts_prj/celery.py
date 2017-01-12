# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
import os
import pickle
from celery import Celery
from celery import shared_task
from salts.tankmanager import tank_manager
from salts_prj.requesthelper import test_connection

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


@shared_task
def obtain_active_tanks(fpath, tanks, http_host):
    active_tanks = []
    for t in tanks:
        tank_host = t["fields"]["host"]
        tank_port = t["fields"]["port"]
        # проверяем, доступен ли с сервера salts хост с танком
        available = test_connection(tank_host, tank_port)
        if available:
            hh = http_host.split(":")
            (host, port) = (hh[0], 80)
            if len(hh) > 1:
                port = hh[1]
            # проверяем, доступен ли с хоста с танком сервер salts
            if test_connection(host, port, tank_host):
                active_tanks.append(t["pk"])
    with open(fpath, "wb") as f:
        pickle.dump(active_tanks, f)
    return os.path.exists(fpath)
