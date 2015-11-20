# -*- coding: utf-8 -*-

import os
import simplejson as json
import logging
import time
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
# from salts_prj.tankapi_client import tankapi_client
from salts_prj.api_client import TankClient


LT_PATH = "/home/krylov/prj/test-repo"
SERVER_HOST_DEFAULT = "salt-dev"
SERVER_PORT_DEFAULT = "8888"


logger = logging.getLogger("salts")
clients = {}
transitions = {"prepare": "finished", "finished": ""}

def ini_files():
    ini = []
    for root, dirs, files in os.walk(LT_PATH, topdown=False):
        for name in files:
            full_path = os.path.join(root, name)
            file_name, file_ext = os.path.splitext(full_path)
            if file_ext == ".ini":
                ini.append(full_path)
    return ini

def is_valid_request(request, keys):
    for k in keys:
        if not request.POST.has_key(k):
            logger.warning("Request hasn't '%s' key." % k)
            return False
    return True

def run_test_api(request):
    if not is_valid_request(request, ["ini_path"]):
        return HttpResponse("Request isn't valid.")

    path = request.POST["ini_path"]
    if path in clients:
        msg = "Client for %s config exist already." % path
        logger.warning(msg)
        return HttpResponse(msg)

    clients[path] = {}
    clients[path]["client"] = TankClient(SERVER_HOST_DEFAULT,
                                         SERVER_PORT_DEFAULT,
                                         logger)
    client = clients[path]["client"]
    resp = ""
    with open(path, "r") as ini_file:
        resp = client.run(ini_file.read(), "start")
    if not resp:
        clients.pop(path, None)
        msg = "No server response when test tried to start."
        logger.warning(msg)
        return HttpResponse(msg)

    logger.info("Response: %s" % resp)
    clients[path]["session"] = resp["session"]

    response_dict = {}
    response_dict.update({"ini_path": path})
    response_dict.update({"wait_status": "prepare"})
    response_dict.update({"session": resp["session"]})
    logger.info("JSON: %s" % json.dumps(response_dict))

    return HttpResponse(json.dumps(response_dict),
                        mimetype="application/javascript")

def stop_test_api(request):
    if not is_valid_request(request, ["ini_path"]):
        return HttpResponse("Request isn't valid.")

    path = request.POST["ini_path"]
    if path not in clients:
        msg = "Client for %s config isn't created." % path
        logger.warning(msg)
        return HttpResponse(msg)

    client = clients[path]["client"]
    client.stop(clients[path]["session"])
    clients.pop(path, None)
    response_dict = {}
    return HttpResponse(json.dumps(response_dict),
                        mimetype="application/javascript")

def status_test_api(request):
    if not is_valid_request(request, ["ini_path", "session", "wait_status"]):
        return HttpResponse("Request isn't valid.")

    path = request.POST["ini_path"]
    if path not in clients:
        msg = "Client for %s config isn't created." % path
        logger.warning(msg)
        return HttpResponse(msg)

    wait_status = request.POST["wait_status"]
    client = clients[path]["client"]
    session = request.POST["session"]
    logger.info("Wait status is %s" % wait_status);
    status = client.status(session)
    logger.info("Status Result is %s" % status)
    resp = None
    if session in status and status[session]["current_stage"] == wait_status:
        if status[session]["stage_completed"]:
            resp = client.resume(session)
            logger.info("Status_test_api: response: %s" % resp)
            wait_status = transitions[wait_status]
            if not wait_status:
                clients.pop(path, None)
    response_dict = {}
    response_dict.update({"ini_path": path})
    response_dict.update({"wait_status": wait_status})
    response_dict.update({"session": session})
    return HttpResponse(json.dumps(response_dict),
                        mimetype="application/javascript")

def tests_list(request):
    clients = {}
    context = {}
    context["configs"] = []
    i = 1
    for name in ini_files():
        context["configs"].append({"name": name,
                                   "id": "%d" % i})
        i += 1
    context.update(csrf(request))
    return render_to_response("tests_list.html", context)
