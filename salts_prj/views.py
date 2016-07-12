# -*- coding: utf-8 -*-

import os
import simplejson as json
import logging
import time
import ConfigParser
import codecs
import re
import pickle
import getpass
from operator import itemgetter

from django.contrib.auth.decorators import login_required
from django.contrib.auth import views
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from salts_prj.api_client import TankClient

from django.forms.formsets import formset_factory
from django.core.paginator import Paginator
from django.views.generic.list import ListView
from django.views.decorators.cache import never_cache
from django.core.cache import caches
from salts.models import (TestSettings, RPS, Target,
                          Generator, TestRun, TestResult, Tank, Shooting)
from salts.forms import SettingsEditForm, RPSEditForm
from salts.tankmanager import tank_manager
from salts_prj.ini import ini_manager
from salts_prj.forms import TestResultEditForm
from settings import (LT_PATH, LT_GITLAB, LT_JIRA, DATABASES,
                      BASE_DIR, VERSION_FILE_NAME)
from requests import ConnectionError


def request_get_value(request, param):
    value = None
    if param in request.GET:
        value = request.GET[param]
    return value


def set_version(response):
    version_path = "%s/%s" % (BASE_DIR, VERSION_FILE_NAME)
    if os.path.exists(version_path):
        with open(version_path, "r") as ver_file:
            v = ver_file.readlines()[0]
            v = v.rstrip("\n")
        if v:
            response["X-Version"] = v


class TestSettingsPaginator(Paginator):

    def __init__(self, object_list, per_page, orphans=0,
                 allow_empty_first_page=True):
        Paginator.__init__(self, object_list, per_page, orphans,
                           allow_empty_first_page)
        self._count = len(list(object_list))


class TestSettingsList(ListView):
    template_name = "testsettings_list.html"
    queryset = TestSettings.objects.raw("SELECT ts.id, ts.test_name, \
ts.file_path, g.host, g.port, g.tool FROM salts_testsettings ts \
JOIN salts_generator g ON ts.generator_id = g.id \
ORDER BY g.tool, ts.test_name")
    # paginate_by = 10
    # paginator_class = TestSettingsPaginator

    def get_context_data(self, **kwargs):
        context = super(TestSettingsList, self).get_context_data(**kwargs)
        # logger.warning("Context: %s" % context)
        return context


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


class TankConfigError(Exception):
    pass


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


def is_valid_request(request, keys):
    for k in keys:
        if not request.POST.has_key(k):
            logger.warning("Request hasn't '%s' key." % k)
            return False
    return True


def run_test_api(request):
    if not is_valid_request(request, ["tsid"]):
        return HttpResponse("Request isn't valid.")

    sess = pickle.loads(request.session["test_run"])


    tsid = request.POST["tsid"]
    if tsid in sess:
        msg = "FUNC run_test_api: client with id=%s exist already." % tsid
        logger.warning(msg)
        return HttpResponse(msg)

    ts_record = TestSettings.objects.get(id=tsid)
    path = os.path.join(LT_PATH, ts_record.file_path)
    qs = TestSettings.objects.raw("SELECT g.id, g.host, g.port \
FROM salts_generator g \
JOIN salts_testsettings ts ON g.id = ts.generator_id WHERE ts.id = %s" % tsid)

    (gen_id, host, port) = (qs[0].id, qs[0].host, qs[0].port)
    client = TankClient(host, port, logger)
    sess[tsid] = {}
    sess[tsid]["host"] = host
    sess[tsid]["port"] = port
    with open(path, "r") as ini_file:
        tr = TestRun(generator_id=gen_id, test_settings_id=tsid, status=TestRun.STATUS_RUNNING)
        tr.save()
        resp = client.run(ini_file.read(), "start", tr.id)
        if not resp:
            msg = "No server response when test tried to start."
            logger.warning(msg)
            return HttpResponse(msg)
        else:
            sess[tsid]["trid"] = tr.id

    sess[tsid]["session"] = resp["session"]
    sess[tsid]["wait_status"] = "prepare"
    request.session["test_run"] = str(pickle.dumps(sess))

    response_dict = {}
    response_dict.update({"ini_path": path})
    response_dict.update({"wait_status": "prepare"})
    response_dict.update({"session": resp["session"]})

    return HttpResponse(json.dumps(response_dict),
                        content_type="application/json")


def stop_test_api(request):
    if not is_valid_request(request, ["tsid"]):
        return HttpResponse("Request isn't valid.")

    sess = pickle.loads(request.session["test_run"])

    tsid = request.POST["tsid"]
    if tsid not in sess:
        msg = "FUNC stop_test_api: client with id=%s isn't exist yet." % tsid
        return HttpResponse(msg)


    host = sess[tsid]["host"]
    port = sess[tsid]["port"]
    client = TankClient(host, port, logger)
    client.stop(sess[tsid]["session"])
    request.session["test_run"] = str(pickle.dumps(sess))
    response_dict = {}
    return HttpResponse(json.dumps(response_dict),
                        content_type="application/json")


def status_info(tsid_info):
    host = tsid_info["host"]
    port = tsid_info["port"]
    client = TankClient(host, port, logger)
    session_id = tsid_info["session"]
    status = client.status(session_id)
    resp = None
    wait_status = tsid_info["wait_status"]
    if session_id in status:
        cur_status = status[session_id]["status"]
        tsid_info["status"] = cur_status
        if status[session_id]["stage_completed"]:
            resp = client.resume(session_id)
        if not (cur_status == "running"):
            tr = TestRun.objects.get(id=tsid_info["trid"])
            tr.status = TestRun.STATUS_DONE
            tr.save()
            return False
    return True


def status_test_api(request):
    if not is_valid_request(request, ["tsid"]):
        return HttpResponse("Request isn't valid.")

    sess = pickle.loads(request.session["test_run"])

    tsid = request.POST["tsid"]
    if tsid not in sess:
        response_dict = {}
        response_dict.update({"tsid": tsid})
        response_dict.update({"run_status": 0})
        return HttpResponse(json.dumps(response_dict),
                            content_type="application/json")
    r = status_info(sess[tsid])
    wait_status = sess[tsid]["wait_status"]
    status = sess[tsid]["status"]
    session = sess[tsid]["session"]
    if not r:
        del sess[tsid]

    request.session["test_run"] = str(pickle.dumps(sess))
    response_dict = {}
    response_dict.update({"tsid": tsid})
    response_dict.update({"wait_status": wait_status})
    response_dict.update({"session": session})
    response_dict.update({"status": status})
    return HttpResponse(json.dumps(response_dict),
                        content_type="application/json")


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
        if len(full_addr) < 2:
            raise TankConfigError("Не указан порт у target.")
        return (rps_value, full_addr[0], full_addr[1])
    else:
        rampup = config.get(sec, "rampup")
        testlen = config.get(sec, "testlen")
        rampdown = config.get(sec, "rampdown")
        rps1 = config.get(sec, "rps1")
        rps2 = config.get(sec, "rps2")
        if not rps1 == rps2:
            raise TankConfigError("rps1 и rps2 должны быть равны.")
        rps_value = "(%s,%s,%s,%s)" % (rps1, rampup, testlen, rampdown)
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
    entity = {"ts": None, "tool": []}
    try:
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
        if not lt_tool:
            logger.info("%s ini-file isn't config for tank test." % full_path)
            logger.warning("FUNC check_changes: %s ini-file isn't config for tank test." % full_path)
            return
        file_name = full_path.replace("%s/" % LT_PATH, "")
        try:
            ts_record = TestSettings.objects.get(file_path=file_name)
        except TestSettings.DoesNotExist:
            ts_record = TestSettings(file_path=file_name, test_name = "",
                                    generator_id=localhost_generator_id(lt_tool),
                                    ticket="", version="")
            ts_record.save()
        entity["ts"] = ts_record
        for sec in tool_sections:
            (rps_value,
                target_host,
                target_port) = get_config_values(config, sec, lt_tool)
            tool_ent = {}
            try:
                target = Target.objects.get(host=target_host, port=target_port)
            except Target.DoesNotExist:
                target = Target(host=target_host, port=target_port)
                target.save()
                tool_ent["target"] = target
            try:
                rps = RPS.objects.get(test_settings_id=ts_record.id,
                                        rps_name=sec)
            except RPS.DoesNotExist:
                rps = RPS(test_settings_id=ts_record.id,
                            rps_name=sec, schedule=rps_value,
                            target_id=target.id)
                rps.save()
            else:
                if not rps.target_id:
                    rps.target_id = target.id
                if not rps.schedule == rps_value:
                    rps.schedule = rps_value
                rps.save()
            tool_ent["rps"] = rps
        entity["tool"].append(tool_ent)
        sec = "sputnikreport"
        ts_record.test_name = config.get(sec, "test_name")
        ts_record.ticket = config.get(sec, "ticket_url")
        ts_record.version = config.get(sec, "version")
        ts_record.save()
        qs = RPS.objects.filter(test_settings_id=ts_record.id).exclude(rps_name__in=tool_sections).delete()
        return
    except ConfigParser.NoOptionError as e:
        logger.warning("Config Parse Issue: %s. Ini-file: %s." %  (e,
                                                                   full_path))
    except ConfigParser.NoSectionError as e:
        logger.warning("Config Parse Issue: %s. Ini-file: %s." %  (e,
                                                                   full_path))
    except ConfigParser.MissingSectionHeaderError as e:
        logger.warning("Config Parse Issue: %s. Ini-file: %s." %  (e,
                                                                   full_path))
    except TankConfigError as e:
        logger.warning("Config Parse Issue: %s. Ini-file: %s." %  (e,
                                                                   full_path))
    for tool_ent in entity["tool"]:
        if "target" in tool_ent:
            tool_ent["target"].delete()
        tool_ent["rps"].delete()
    if entity["ts"]:
        entity["ts"].delete()


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


def poll_servers(request):
    response_dict = {}
    if "test_run" in request.session:
        del request.session["test_run"]
    tr_session = {}
    generators = Generator.objects.all().values("host", "port").distinct()
    for gen in generators:
        client = TankClient(gen["host"], gen["port"], logger)
        try:
            data = client.status()
        except ConnectionError as e:
            continue
        sessions = data.keys()
        for sess in sessions:
            test_id = sess.replace("_0000000000", "")
            try:
                tr = TestRun.objects.get(id=test_id)
            except TestRun.DoesNotExist:
                continue
            ts = TestSettings.objects.get(id=tr.test_settings_id)
            tsid = str(ts.id)
            is_write = False
            if tsid in tr_session:
                if tr.id > int(tr_session[tsid]["trid"]):
                    is_write = True
            else:
                is_write = True
            if is_write:
                tr_session[tsid] = {}
                tr_session[tsid]["host"] = gen["host"]
                tr_session[tsid]["port"] = gen["port"]
                tr_session[tsid]["session"] = sess
                tr_session[tsid]["wait_status"] = "prepare"
                tr_session[tsid]["trid"] = tr.id
    for tsid in tr_session:
        r = status_info(tr_session[tsid])
        test_run = {}
        test_run.update({"wait_status": tr_session[tsid]["wait_status"]})
        test_run.update({"session": tr_session[tsid]["session"]})
        test_run.update({"status": tr_session[tsid]["status"]})
        if r:
            test_run.update({"run_status": "1"})
        else:
            test_run.update({"run_status": "0"})
        response_dict.update({tsid: test_run})
    remove_ids = [id for id in tr_session if not (tr_session[id]["status"] == "running")]
    for id in remove_ids:
         tr_session[id]
    request.session["test_run"] = str(pickle.dumps(tr_session))
    return HttpResponse(json.dumps(response_dict),
                        content_type="application/json")


def set_context(request):
    context = {}
    context.update(csrf(request))
    context["host"] = DATABASES["default"]["HOST"]
    context["name"] = DATABASES["default"]["NAME"]
    return context


def generate_context(request):
    context = {}
    context.update(csrf(request))
    context['host'] = DATABASES['default']['HOST']
    context['name'] = DATABASES['default']['NAME']
    context['username'] = request.user.username
    context['is_superuser'] = request.user.is_superuser
    context['is_staff'] = request.user.is_staff
    return context


@login_required
def show_results_page(request):
    context = generate_context(request)
    response = render_to_response('testresult_list.html', context)
    set_version(response)
    return response


@never_cache
@login_required
def tank_monitoring(request):
    context = generate_context(request)
    response = render_to_response('tank_monitoring.html', context)
    set_version(response)
    return response


def show_trends_page(request):
    context = generate_context(request)
    response = render_to_response("graph_trends.html", context)
    set_version(response)
    return response


def user_filter(request, results):
    scen_id = request_get_value(request, "scid")
    target = request_get_value(request, "trg")
    gen_type = request_get_value(request, "gt")
    generator = request_get_value(request, "gen")
    test_group = request_get_value(request, "tg")
    test_search = request_get_value(request, "ts")
    status = request_get_value(request, "st")
    task_id = request_get_value(request, "tid")
    spe = request_get_value(request, "spe")
    from_time = request_get_value(request, "from")
    to_time = request_get_value(request, "to")
    rps_value = request_get_value(request, "rps")
    if scen_id:
        results = results.filter(scenario_id=scen_id)
    if target:
        results = results.filter(target__contains=target)
    if test_group:
        results = results.filter(group=test_group)
    if test_search:
        results = results.filter(test_name__contains=test_search)
    if gen_type:
        results = results.filter(generator_types__name__contains=gen_type)
    if generator:
        results = results.filter(generator__contains=generator)
    if rps_value:
        results = results.filter(rps=rps_value)
    if status:
        status = status.split(",")
        for (i, item) in enumerate(status):
            if item == "unknown":
                status[i] = u"unk"
            if item == "debug":
                status[i] = u"dbg"
        results = results.filter(test_status__in=status)
    if task_id:
        results = results.filter(ticket_id=task_id)
    if spe:
        results = results.filter(user=spe)
    if from_time:
        from_time = from_time.replace("_", " ")
        results = results.filter(dt_finish__gte=from_time)
    if to_time:
        to_time = to_time.replace("_", " ")
        results = results.filter(dt_finish__lte=to_time)
    return results


def edit_page_url(request, test_result_user):
    if request.user.is_staff or request.user.is_superuser:
        return "/admin/salts/testresult/?id="
    if request.user.username == test_result_user:
        return "/edit/?id="
    return ''


def get_results(request):
    results = TestResult.objects.extra(select={"http_net": "http_errors_perc || '/' || net_errors_perc",
                                               "duration": "to_char(dt_finish - dt_start, 'HH24:MI:SS')",
                                               "dt_finish": "to_char(dt_finish at time zone 'MSK', 'YYYY-MM-DD HH24:MI:SS')",
                                               "comment": "comments"})
    results = results.values("id", "test_name", "target", "version", "rps", "q99",
                             "q90", "q50", "graph_url", "generator",
                             "dt_finish", "test_id", "scenario_id", "group",
                             "test_status", "ticket_id", "user", "duration",
                             "http_net", "comment")
    results = user_filter(request, results)
    sort_param = request_get_value(request, "sort")
    if sort_param:
        order = request_get_value(request, "order")
        if not order:
            order = "asc"
        if order == "asc":
            results = results.order_by(sort_param)
        else:
            results = results.order_by("-%s" % sort_param)
    query = """SELECT tmp.id, STRING_AGG(tmp.name, ' ') gen_type_list FROM
                        ( SELECT trgt.testresult_id id, gt.name FROM salts_testresult_generator_types trgt
                          JOIN salts_generatortype gt ON trgt.generatortype_id = gt.id
                          GROUP BY testresult_id, name
                          ORDER BY testresult_id, name
                        ) tmp
                GROUP BY id
            """
    gen_types_results = TestResult.objects.raw(query)
    gen_types = {}
    for r in gen_types_results:
        gen_types[r.id] = r.gen_type_list
    results = list(results)
    for r in results:
        if r["id"] in gen_types:
            r["gen_type_list"] = gen_types[r["id"]]
        else:
            r["gen_type_list"] = ""
        r["generator"] = "%s / %s" % (r["generator"], r["gen_type_list"])
        r['edit_url'] = edit_page_url(request, r['user'])

    offset = request_get_value(request, "offset")
    limit = request_get_value(request, "limit")

    response_dict = {}
    response_dict["total"] = len(results)
    if offset and limit:
        offset = int(offset)
        limit = int(limit)
        results = results[offset:offset+limit]
    response_dict["rows"] = results

    response = HttpResponse(json.dumps(response_dict),
                            content_type="application/json")
    set_version(response)
    return response


def get_remained_time(shooting):
    remained = 0
    if shooting.planned_duration:
        if shooting.planned_duration == -1:
            return -1
        if shooting.start:
            if shooting.status == 'I':
                ts = shooting.finish
                if not ts:
                    ts = shooting.start
            else:
                ts = int(time.time() + 0.5)
            if shooting.status == 'P':
                remained = shooting.planned_duration
            else:
                remained = shooting.planned_duration - (ts - shooting.start)
        else:
            remained = shooting.planned_duration
    if remained < 0:
        remained = 0

    return remained


@never_cache
def get_tank_status(request):
    logger.info("get_tank_status: request.GET: %s" % request.GET)
    tank_id = request.GET.get('tank_id')
    if tank_id:
        tanks = Tank.objects.filter(id=tank_id)
    else:
        tanks = Tank.objects.all()
    results = []
    for t in tanks:
        shooting = t.shooting_set.exclude(start__isnull=True).order_by('-start').first()
        if not shooting:
            continue
        username = ''
        if shooting.user:
            if shooting.user.username == 'ltbot':
                username = shooting.alt_name        # временно, для консольных
                                                    # тестов, чтобы обойти
                                                    # аутентификацию
            else:
                username = shooting.user.username
        scen_id = shooting.test_ini.scenario_id
        values = {'id': t.id, 'host': t.host,
                  'username': username,
                  'gitlab_url': '%s%s' % (LT_GITLAB,
                                          shooting.test_ini.scenario_id),
                  'scenario_name': ini_manager.get_scenario_name(scen_id),
                  'status': shooting.status,
                  'countdown': get_remained_time(shooting),
                  'shooting_id': shooting.id,
                  'ticket_id': shooting.ticket_id}
        port = tank_manager.read_from_lock(t.id, 'web_console_port')
        if port:
            values['webconsole'] = "%s:%s" % (t.host, port)
        if shooting.ticket_id:
            values['ticket_url'] = '%s%s' % (LT_JIRA, shooting.ticket_id)
        if shooting.status in ['F', 'I']:
            tr = TestResult.objects.filter(test_id=shooting.test_id)
            if tr:
                values['test_result'] = tr[0].id
        results.append(values)
    sort_param = request_get_value(request, 'sort')
    if sort_param:
        order = request_get_value(request, 'order')
        if not order:
            order = 'asc'
        reverse = order == 'desc'
        results = sorted(results, key=itemgetter('id'), reverse=reverse)

    response_dict = {}
    response_dict['total'] = len(results)
    response_dict['rows'] = results
    response = HttpResponse(json.dumps(response_dict),
                            content_type='application/json')
    set_version(response)
    return response


@never_cache
def salts_logout(request):
    context = {}
    context['info'] = u"Вы успешно вышли"
    response = views.logout(request,
                            template_name="registration/login.html",
                            extra_context=context)
    response = views.login(request,
                           template_name="registration/login.html",
                           extra_context=context)
    set_version(response)
    return response


@never_cache
def edit_testresult(request):
    id = request.GET['id']
    tr = TestResult.objects.get(id=id)
    context = {}
    context.update(csrf(request))
    context['test_name'] = tr.test_name
    context['form'] = TestResultEditForm(instance=tr)
    context['next'] = request.META.get('HTTP_REFERER')
    context['id'] = id
    return render_to_response("testresult_edit.html", context)


def add_get_parameters(url, params):
    import urlparse
    from urllib import urlencode

    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(params)

    url_parts[4] = urlencode(query)
    return urlparse.urlunparse(url_parts)


@never_cache
def update_testresult(request):
    redirect_url = request.POST.get('next')
    if request.POST.get('save'):
        tr = TestResult.objects.get(id=request.POST.get('id'))
        tr.test_status = request.POST.get('test_status')
        tr.comments = request.POST.get('comments')
        tr.save()
        caches['default'].clear()
        redirect_url = add_get_parameters(redirect_url, {'cc': 0})
    return HttpResponseRedirect(redirect_url)


def gitsync(request):
    logger.info("gitsync calling")
    return HttpResponse(status=200)
