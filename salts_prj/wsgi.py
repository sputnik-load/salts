#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
"""
WSGI config for salts project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "salts_prj.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from salts_prj.settings import LT_PATH, EXCLUDE_INI_FILES
from salts_prj.ini import IniCtrl
ini_ctrl = IniCtrl(LT_PATH, EXCLUDE_INI_FILES)
ini_ctrl.sync()
