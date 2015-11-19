# -*- coding: utf-8 -*-

import os
import simplejson
import logging
import time
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from salts_prj.tankapi_client import tankapi_client


LT_PATH = "/home/krylov/prj/test-repo"
SERVER_HOST_DEFAULT = "localhost"
SERVER_PORT_DEFAULT = "8888"


logger = logging.getLogger("salts")

def ini_files():
    ini = []
    for root, dirs, files in os.walk(LT_PATH, topdown=False):
        for name in files:
            full_path = os.path.join(root, name)
            file_name, file_ext = os.path.splitext(full_path)
            if file_ext == ".ini":
                ini.append(full_path)
    return ini


def run_test_api(ini_path):
    client1 = tankapi_client.tankapi_client(SERVER_HOST_DEFAULT,
                                            SERVER_PORT_DEFAULT,
                                            logger)
    logger.info("Preparing ...")
    shoot1 = client1.run_new(config_contents=ini_path,
                             stage="start")
    logger.info(shoot1)
    while not client1.destination_reached(shoot1["session"], "prepare"):
        logger.info("Test not prepared yet.")
        time.sleep(5)
    logger.info("Prepared OK")
    logger.info("Shooting ...")
    client1.run_given(shoot1["session"])
    while not client1.destination_reached(shoot1["session"], "finished"):
        logger.info("Test not finished yet.")
        time.sleep(5)

def tests_list(request):
    if request.POST.has_key("client_response"):
        x = request.POST["ini_path"]
        response_dict = {}
        response_dict.update({"server_response": x})
        return HttpResponse(simplejson.dumps(response_dict),
                            mimetype="application/javascript")
    context = {}
    context["configs"] = []
    i = 1
    for name in ini_files():
        context["configs"].append({"name": name,
                                   "id": "%d" % i})
        i += 1
    context.update(csrf(request))
    return render_to_response("tests_list.html", context)
