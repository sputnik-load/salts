# -*- coding: utf-8 -*-

import os
import simplejson
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.core.context_processors import csrf


LT_PATH = "/home/krylov/prj/loadtest"


def ini_files():
    ini = []
    for root, dirs, files in os.walk(LT_PATH, topdown=False):
        for name in files:
            full_path = os.path.join(root, name)
            file_name, file_ext = os.path.splitext(full_path)
            if file_ext == ".ini":
                ini.append(full_path)
    return ini


def tests_list(request):
    if request.POST.has_key("client_response"):
        x = request.POST["client_response"]
        response_dict = {}
        response_dict.update({"server_response": x})
        # response_dict.update({"csrftoken": request.POST["csrfmiddlewaretoken"]})
        return HttpResponse(simplejson.dumps(response_dict),
                            mimetype="application/javascript")
    context = {}
    context["configs"] = []
    i = 1
    for name in ini_files():
        context["configs"].append({"name": name,
                                   "id": "ini_%d" % i})
        i += 1
    context.update(csrf(request))
    return render_to_response("tests_list.html", context)
