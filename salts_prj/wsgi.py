#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
"""
WSGI config for salts project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
import json
from django.core import serializers
from salts_prj.requesthelper import test_connection
from salts.models import Tank
from salts_prj.settings import HTTP_HOST, LOCK_PATH
import pickle

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "salts_prj.settings")

application = get_wsgi_application()


tanks = Tank.objects.all()
jtanks = json.loads(serializers.serialize("json", tanks))
active_tanks = []
for t in jtanks:
    tank_host = t["fields"]["host"]
    tank_port = t["fields"]["port"]
    # проверяем, доступен ли с сервера salts хост с танком
    available = test_connection(tank_host, tank_port)
    if available:
        hh = HTTP_HOST.split(":")
        (host, port) = (hh[0], 80)
        if len(hh) > 1:
            port = hh[1]
        # проверяем, доступен ли с хоста с танком сервер salts
        if test_connection(host, port, tank_host):
            active_tanks.append(t["pk"])

fpath = os.path.join(LOCK_PATH, "tanks")
with open(fpath, "wb") as f:
    pickle.dump(active_tanks, f)
