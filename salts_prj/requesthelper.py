# -*- coding: utf-8 -*-

import requests
import socket
import time
from os.path import exists
from salts_prj.settings import log
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
    from django.core.context_processors import csrf
    context = {}
    context.update(csrf(request))
    context['host'] = DATABASES['default']['HOST']
    context['name'] = DATABASES['default']['NAME']
    context['username'] = request.user.username
    context['is_superuser'] = request.user.is_superuser
    context['is_staff'] = request.user.is_staff
    return context


def test_connection(target, port, hname=None):
    try:
        if hname:
            req = "http://{hname}:5000/conn?target={target}&port={port}"
            resp = requests.get(req.format(hname=hname, target=target,
                                           port=port))
            return float(resp.content)
        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            st = time.time()
            s.connect((target, port))
            s.close()
            return time.time() - st
    except Exception, exc:
        if not hname:
            hname = "localhost"
        log.warning("The connection from %s to %s:%s is impossible due to %s. "
                    % (hname, target, port, exc))
        return 0.0


def log_message(msg):
    log.info(msg)
