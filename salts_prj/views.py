import os
import simplejson as json
import logging
import time
import ConfigParser
import codecs
import re

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from salts_prj.api_client import TankClient

from django.forms.formsets import formset_factory

from django.views.generic.list import ListView
from salts.models import TestSettings, RPS, Target
from salts.forms import SettingsEditForm, RPSEditForm


LT_PATH = "/home/krylov/prj/test-repo"
SERVER_HOST_DEFAULT = "localhost"
SERVER_PORT_DEFAULT = "8888"

class TestSettingsList(ListView):
    model = TestSettings

class UnicodeConfigParser(ConfigParser.RawConfigParser):
    def __init__(self, *args, **kwargs):
        ConfigParser.RawConfigParser.__init__(self, *args, **kwargs)

    def write(self, fp):
        """Fixed for Unicode output"""
        if self._defaults:
            fp.write("[%s]\n" % "DEFAULT")
            for (key, value) in self._defaults.items():
                fp.write("%s = %s\n" % (key, unicode(value).replace('\n', '\n\t')))
            fp.write("\n")

        for section in self._sections:
            fp.write("[%s]\n" % section)
            for (key, value) in self._sections[section].items():
                if key != "__name__":
                    fp.write("%s = %s\n" % (key, unicode(value).replace('\n','\n\t')))
            fp.write("\n")

    # This function is needed to override default lower-case conversion
    # of the parameter's names. They will be saved 'as is'.
    def optionxform(self, strOut):
        return strOut


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

    path = os.path.join(LT_PATH, request.POST["ini_path"])
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


def edit_test_parameters(request, settings_id):
    ts_record = TestSettings.objects.get(id=settings_id)
    settings_form = SettingsEditForm(instance=ts_record)
    rps_record = RPS.objects.filter(test_settings_id=settings_id)
    RpsFormSet = formset_factory(RPSEditForm, extra=0)
    # logger.info("rps_record: %s" % rps_record)
    data = []
    rps_id = []
    for record in rps_record:
        rps_id.append(str(record.id))
        logger.info("RPS Edit Form: %s" % record.rps_name)
        data.append({"target": record.target, "rps_name": record.rps_name,
                     "schedule": record.schedule})
        # rps_form = RPSEditForm(instance=record)
    formset = RpsFormSet(initial=data)
    context = {}
    context.update(csrf(request))
    context.update({"settings_form": settings_form,
                    "rps_form": formset,
                    "settings": settings_id,
                    "rpsid": ",".join(rps_id)})
    return render_to_response("testsettings_edit.html", context)


def get_config_values(config, sec, is_phantom):
    if is_phantom:
        rps_value = config.get(sec, "rps_schedule")
        full_addr = config.get(sec, "address").split(":")
        return (rps_value, full_addr[0], full_addr[1])
    else:
        rampup = config.get(sec, "rampup")
        testlen = config.get(sec, "testlen")
        rampdown = config.get(sec, "rampdown")
        rps = config.get(sec, "rps1")
        rps_value = "(%s,%s,%s,%s)" % (rps, rampup, testlen, rampdown)
        target = config.get(sec, "hostname")
        port = config.get(sec, "port")
        return (rps_value, target, port)

def check_changes(file_path):
    logger.info("File Path: %s" % file_path)
    file_name = file_path.replace("%s/" % LT_PATH, "")
    qs = TestSettings.objects.filter(file_path=file_name)
    if not qs:
        return

    record = qs[0]

    logger.info("Record: %s" % record)
    config = ConfigParser.RawConfigParser()
    config.read(file_path)
    rps_qs = RPS.objects.filter(test_settings_id=record.id)
    logger.info("rps_values: %s" % rps_qs)
    jmp = re.compile("jmeter")
    ph = re.compile("phantom")
    tool_name = ""
    tool_sections = []
    for sec in config.sections():
        is_phantom = ph.match(sec)
        is_jmeter = jmp.match(sec)
        if is_phantom or is_jmeter:
            tool_sections.append(sec)
            (rps_value, target_host, target_port) = get_config_values(config, sec, is_phantom)
            try:
                target = Target.objects.get(host=target_host, port=target_port)
            except Target.DoesNotExist:
                target = Target(host=target_host, port=target_port)
                target.save()
                logger.info("New target was added: %s" % target)

            try:
                r = RPS.objects.get(test_settings_id=record.id,
                                       rps_name=sec)
            except RPS.DoesNotExist:
                rps = RPS(test_settings_id=record.id,
                          rps_name=sec, schedule=rps_value,
                          target_id=target.id)
                rps.save()
                logger.info("New rps was added: %s" % rps)
            else:
                if not r.target_id:
                    r.target_id = target.id
                if not r.schedule == rps_value:
                    r.schedule = rps_value
                r.save()
                logger.info("rps was updated: %s" % r)
        if sec == "sputnikreport":
            test_name = config.get(sec, "test_name")
            ticket = config.get(sec, "ticket_url")
            version = config.get(sec, "version")
    qs = RPS.objects.filter(test_settings_id=record.id).exclude(rps_name__in=tool_sections).delete()


def sync_config(file_path, *args, **kwargs):
    config = UnicodeConfigParser()
    config.readfp(codecs.open(file_path, "r", "utf-8"))
    is_changed = False
    if "test_settings" in kwargs:
        ts_record = kwargs["test_settings"]
        sp_sec = "sputnikreport"
        config.set(sp_sec, "test_name", ts_record.test_name)
        logger.info("INFO: %s" % ts_record.test_name)
        config.set(sp_sec, "ticket_url", ts_record.ticket)
        config.set(sp_sec, "version", ts_record.version)
        is_changed = True
    if "rps" in kwargs:
        ph = re.compile("phantom")
        jmp = re.compile("jmeter")
        rps_record = kwargs["rps"]
        if ph.match(rps_record.rps_name):
            config.set(rps_record.rps_name, "rps_schedule", rps_record.schedule)
            is_changed = True
        elif jmp.match(rps_record.rps_name):
            (rampup, testlen, rampdown, rps) = re.findall("\d+", rps_record.schedule)
            config.set(rps_record.rps_name, "rampup", rampup)
            config.set(rps_record.rps_name, "testlen", testlen)
            config.set(rps_record.rps_name, "rampdown", rampdown)
            config.set(rps_record.rps_name, "rps1", rps)
            config.set(rps_record.rps_name, "rps2", rps)
            is_changed = True
    if is_changed:
        config.write(codecs.open(file_path, "wb", "utf-8"))


def show_test_settings(request):
    if request.method == "GET":
        for file_path in ini_files():
            check_changes(file_path)
        return TestSettingsList.as_view(template_name="testsettings_list.html")(request)
    if request.method == "POST":
        if "cancel-button" in request.POST:
            return HttpResponseRedirect("/tests/")
        logger.info("Request.POST: %s" % request.POST)
        ts_record = TestSettings.objects.get(id=request.POST["settings"])
        config_path = os.path.join(LT_PATH, ts_record.file_path)
        logger.info("ts_record: %s" % ts_record)
        ts_record.test_name = request.POST["test_name"]
        ts_record.ticket = request.POST["ticket"]
        ts_record.version = request.POST["version"]
        ts_record.generator_id = request.POST["generator"]
        ts_record.save()
        sync_config(config_path, test_settings=ts_record)
        rpsid = request.POST["rpsid"].split(",")
        form_id = 0
        for id_rps in rpsid:
            rps_record = RPS.objects.get(id=id_rps)
            rps_record.rps_name = request.POST["form-%d-rps_name" % form_id]
            rps_record.schedule = request.POST["form-%d-schedule" % form_id]
            rps_record.target_id = request.POST["form-%d-target" % form_id]
            rps_record.save()
            sync_config(config_path, rps=rps_record)
            form_id += 1
        return HttpResponseRedirect("/tests/")
