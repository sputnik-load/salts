# -*- coding: utf-8 -*-

from os.path import exists
from django.core.context_processors import csrf
from salts_prj.settings import BASE_DIR, VERSION_FILE_NAME, DATABASES


def request_get_value(request, param):
    value = None
    if param in request.GET:
        value = request.GET[param]
    return value


def read_version():
    version_path = "%s/%s" % (BASE_DIR, VERSION_FILE_NAME)
    if not exists(version_path):
        return ''
    with open(version_path, 'r') as ver_file:
        v = ver_file.readlines()[0]
        v = v.rstrip('\n')
        return v


def add_version(response):
    v = read_version()
    if v:
        response["X-Version"] = v


def generate_context(request):
    context = {}
    context.update(csrf(request))
    context['host'] = DATABASES['default']['HOST']
    context['name'] = DATABASES['default']['NAME']
    context['username'] = request.user.username
    context['is_superuser'] = request.user.is_superuser
    context['is_staff'] = request.user.is_staff
    return context
