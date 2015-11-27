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
from salts.models import TestSettings, RPS, Target, Generator
from salts.forms import SettingsEditForm, RPSEditForm


LT_PATH = "/home/krylov/prj/test-repo"
SERVER_HOST_DEFAULT = "localhost"
SERVER_PORT_DEFAULT = "8888"


class TestSettingsList(ListView):
    template_name = "testsettings_list.html"
    queryset = TestSettings.objects.raw("SELECT ts.id, ts.test_name, \
ts.file_path, g.host, g.port, g.tool FROM salts_testsettings ts \
JOIN salts_generator g ON ts.generator_id = g.id")


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
    if not is_valid_request(request, ["tsid"]):
        return HttpResponse("Request isn't valid.")

    tsid = request.POST["tsid"]
    if tsid in clients:
        msg = "FUNC run_test_api: client with id=%s exist already." % tsid
        logger.warning(msg)
        return HttpResponse(msg)

    ts_record = TestSettings.objects.get(id=tsid)
    path = os.path.join(LT_PATH, ts_record.file_path)
    qs = TestSettings.objects.raw("SELECT g.id, g.host, g.port \
FROM salts_generator g \
JOIN salts_testsettings ts ON g.id = ts.generator_id WHERE ts.id = %s" % tsid)

    logger.debug("Path: %s" % path)
    logger.debug("Generator: %s" % qs)

    clients[tsid] = {}
    clients[tsid]["client"] = TankClient(qs[0].host, qs[0].port, logger)
    client = clients[tsid]["client"]
    resp = ""
    with open(path, "r") as ini_file:
        resp = client.run(ini_file.read(), "start")
    if not resp:
        clients.pop(path, None)
        msg = "No server response when test tried to start."
        logger.warning(msg)
        return HttpResponse(msg)

    logger.info("Response: %s" % resp)
    clients[tsid]["session"] = resp["session"]
    clients[tsid]["wait_status"] = "prepare"

    response_dict = {}
    response_dict.update({"ini_path": path})
    response_dict.update({"wait_status": "prepare"})
    response_dict.update({"session": resp["session"]})
    logger.info("JSON: %s" % json.dumps(response_dict))

    return HttpResponse(json.dumps(response_dict),
                        content_type="application/json")


def stop_test_api(request):
    if not is_valid_request(request, ["tsid"]):
        return HttpResponse("Request isn't valid.")

    tsid = request.POST["tsid"]
    if tsid not in clients:
        msg = "FUNC stop_test_api: client with id=%s isn't exist yet." % tsid
        logger.warning(msg)
        return HttpResponse(msg)

    client = clients[tsid]["client"]
    client.stop(clients[tsid]["session"])
    clients.pop(tsid, None)
    response_dict = {}
    return HttpResponse(json.dumps(response_dict),
                        content_type="application/json")


def status_test_api(request):
    if not is_valid_request(request, ["tsid"]):
        return HttpResponse("Request isn't valid.")

    tsid = request.POST["tsid"]
    if tsid not in clients:
        msg = "FUNC status_test_api: client with id=%s isn't exist yet." % tsid
        logger.debug(msg)
        response_dict = {}
        response_dict.update({"tsid": tsid})
        response_dict.update({"run_status": 0})
        return HttpResponse(json.dumps(response_dict),
                            content_type="application/json")

    client = clients[tsid]["client"]
    session = clients[tsid]["session"]
    status = client.status(session)
    logger.debug("Status Result is %s" % status)
    resp = None
    wait_status = clients[tsid]["wait_status"]
    if session in status and status[session]["current_stage"] == wait_status:
        if status[session]["stage_completed"]:
            resp = client.resume(session)
            logger.debug("Status_test_api: response: %s" % resp)
            wait_status = transitions[wait_status]
            clients[tsid]["wait_status"] = wait_status
            if not wait_status:
                clients.pop(tsid, None)
    response_dict = {}
    response_dict.update({"tsid": tsid})
    response_dict.update({"wait_status": wait_status})
    response_dict.update({"session": session})
    return HttpResponse(json.dumps(response_dict),
                        content_type="application/json")


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


def get_config_values(config, sec, lt_tool):
    if lt_tool == "phantom":
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


def localhost_generator_id(lt_tool):
    try:
        gen_record = Generator.objects.get(host="localhost", port=8888,
                                           tool=lt_tool)
    except Generator.DoesNotExist:
        gen_record = Generator(host="localhost", port=8888, tool=lt_tool)
        gen_record.save()
    return gen_record.id


def check_changes(full_path):
    config = ConfigParser.RawConfigParser()
    config.read(full_path)
    jmp = re.compile("jmeter")
    ph = re.compile("phantom")
    tool_sections = []
    lt_tool = None
    for sec in config.sections():
        if ph.match(sec):
            lt_tool = "phantom"
            tool_sections.append(sec)
        elif jmp.match(sec):
            lt_tool = "jmeter"
            tool_sections.append(sec)
    file_name = full_path.replace("%s/" % LT_PATH, "")
    try:
        ts_record = TestSettings.objects.get(file_path=file_name)
    except TestSettings.DoesNotExist:
        logger.debug("DB: record about %s file is absent." % file_name)
        ts_record = TestSettings(file_path=file_name, test_name = "",
                                 generator_id=localhost_generator_id(lt_tool),
                                 ticket="", version="")
        ts_record.save()
    for sec in tool_sections:
        (rps_value,
            target_host,
            target_port) = get_config_values(config, sec, lt_tool)
        try:
            target = Target.objects.get(host=target_host, port=target_port)
        except Target.DoesNotExist:
            target = Target(host=target_host, port=target_port)
            target.save()
            logger.debug("New target was added: %s" % target)

        try:
            rps = RPS.objects.get(test_settings_id=ts_record.id,
                                    rps_name=sec)
        except RPS.DoesNotExist:
            rps = RPS(test_settings_id=ts_record.id,
                        rps_name=sec, schedule=rps_value,
                        target_id=target.id)
            rps.save()
            logger.debug("New rps was added: %s" % rps)
        else:
            if not rps.target_id:
                rps.target_id = target.id
            if not rps.schedule == rps_value:
                rps.schedule = rps_value
            rps.save()
            logger.debug("rps was updated: %s" % rps)
    sec = "sputnikreport"
    ts_record.test_name = config.get(sec, "test_name")
    ts_record.ticket = config.get(sec, "ticket_url")
    ts_record.version = config.get(sec, "version")
    ts_record.save()
    qs = RPS.objects.filter(test_settings_id=ts_record.id).exclude(rps_name__in=tool_sections).delete()


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
            (rps, rampup, testlen, rampdown) = re.findall("\d+", rps_record.schedule)
            config.set(rps_record.rps_name, "rps1", rps)
            config.set(rps_record.rps_name, "rps2", rps)
            config.set(rps_record.rps_name, "rampup", rampup)
            config.set(rps_record.rps_name, "testlen", testlen)
            config.set(rps_record.rps_name, "rampdown", rampdown)
            is_changed = True
    if is_changed:
        config.write(codecs.open(file_path, "wb", "utf-8"))


def show_test_settings(request):
    if request.method == "GET":
        for file_path in ini_files():
            check_changes(file_path)
        return TestSettingsList.as_view()(request)
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
