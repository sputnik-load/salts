# -*- coding: utf-8 -*-
"""
Django settings for salts_prj project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

from __future__ import absolute_import, unicode_literals

import ConfigParser
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS

HOSTNAME = "<SALTS_HOSTNAME>"
HTTP_HOST = "{}:80".format(HOSTNAME)
CELERY_BROKER_URL = "amqp://salts:salts@{}:5672/salts".format(HOSTNAME)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_RESULT_BACKEND = "db+postgresql://salts:salts@{}/salts".format(HOSTNAME)
CELERY_TASK_SERIALIZER = "json"
CELERY_BROKER_VHOST="salts"

TEMPLATE_CONTEXT_PROCESSORS += (
    'django.core.context_processors.request',
)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

QUNIT_TEST_DIRECTORY = os.path.join(BASE_DIR, 'js_tests')
TEMPLATE_DIRS = [os.path.join(BASE_DIR, "templates"),
                 QUNIT_TEST_DIRECTORY]
QUNIT_INDEX_HTML = "tests.html"

# List of callables that know how to import templates from various sources.import
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'g$#^+$xl7k)b(&uq4li+99w-mdy15k7tsn=^7maguuygibc4r3'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

LOGIN_URL = "login"
LOGOUT_URL = "logout"
LOGIN_REDIRECT_URL = "/results"

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'debug_toolbar',
    'salts',
    'tastypie',
    'rest_framework',
    'rest_framework.authtoken',
    'djangobower',
    'django_extensions',
    'django_qunit'
)

ROOT_URLCONF = 'salts_prj.urls'

WSGI_APPLICATION = 'salts_prj.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'salts',
        'USER': 'salts',
        'PASSWORD': 'salts',
        'HOST': HOSTNAME,    # Empty for localhost through domain sockets or           '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

LT_PATH = '/data/qa/ltbot/loadtest'
LT_GITLAB = 'http://<GITLAB_URL>/loadtest/loadtest/blob/master/'
LT_JIRA = 'https://<JIRA_URL>/browse/'
VERSION_FILE_NAME = 'version'
UWSGI_USER = "uwsgi"
UWSGI_GROUP = "uwsgi"
LOCK_PATH = "/tmp/salts_lock"
EXCLUDE_INI_FILES = ['common.ini', 'user.ini',
                     'graphite*.ini', 'run.sh.ini',
                     '99*.ini', '98*.ini', 'influx*.ini']

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

#LANGUAGE_CODE = 'en-us'
#TIME_ZONE = 'UTC'
TIME_ZONE = 'Europe/Moscow'
LANGUAGE_CODE = 'ru-RU'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_ROOT = os.path.join(BASE_DIR, "media/")
MEDIA_URL = '/media/'

BOWER_COMPONENTS_ROOT = os.path.join(BASE_DIR, 'components')

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'djangobower.finders.BowerFinder',
)

BOWER_INSTALLED_APPS = (
    "bootstrap-table#1.11.1",
    "x-editable#1.5.1",
    "purl#2.3.1",
    "bootstrap#3.3.6",
    "https://github.com/burthen/dygraphs.git#1.1.2",
    "moment#2.11.2",
    "qunit#2.1.1"
)

DEBUG_TOOLBAR_PATCH_SETTINGS = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'logfile': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR + "/logfile",
            'maxBytes': 1024 * 1024,
            'backupCount': 5,
            'formatter': 'standard',
        },
        'console':{
            'level':'INFO',
            'class':'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django': {
            'handlers':['console'],
            'propagate': True,
            'level':'WARN',
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARN',
            'propagate': False,
        },
        'salts': {
            'handlers': ['console', 'logfile'],
            'level': 'INFO',
        },
    }
}

import logging
log = logging.getLogger('salts')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}


DEBUG_SETTINGS_NAME = 'debug_settings.ini'
debug_settings_path = '%s/%s' % (os.path.dirname(os.path.realpath(__file__)), DEBUG_SETTINGS_NAME)
cache_on = True
if os.path.exists(debug_settings_path):
    cfg = ConfigParser.RawConfigParser()
    cfg.read(debug_settings_path)
    sections = cfg.sections()
    if "database" in sections:
        for k in DATABASES['default']:
            DATABASES['default'][k] = cfg.get('database', k)
    if 'cache' in sections:
        if 'on' in cfg.options('cache') and cfg.get('cache', 'on') != '1':
            cache_on = False
    if 'repo' in sections:
        options = cfg.options('repo')
        if 'lt_path' in options:
            LT_PATH = cfg.get('repo', 'lt_path')
        if 'lt_gitlab' in options:
            LT_GITLAB = cfg.get('repo', 'lt_gitlab')
    if 'celery' in sections:
        options = cfg.options('celery')
        if 'broker_url' in options:
            CELERY_BROKER_URL = cfg.get('celery', 'broker_url')
        if 'broker_vhost' in options:
            CELERY_BROKER_VHOST = cfg.get('celery', 'broker_vhost')
        if 'result_backend' in options:
            CELERY_RESULT_BACKEND = cfg.get('celery', 'result_backend')

if cache_on:
    MIDDLEWARE_CLASSES = (
        'django.middleware.cache.UpdateCacheMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'audit_log.middleware.UserLoggingMiddleware',
        'django.middleware.cache.FetchFromCacheMiddleware',
    )
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': '/var/tmp/django_cache',
            'TIMEOUT': 300,
            'OPTIONS': {
                'MAX_ENTRIES': 1000
            }
        }
    }
else:
    MIDDLEWARE_CLASSES = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'audit_log.middleware.UserLoggingMiddleware',
    )
