# -*- coding: utf-8 -*-

from os.path import exists
from salts_prj.settings import BASE_DIR, VERSION_FILE_NAME


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
