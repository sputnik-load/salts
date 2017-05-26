# -*- coding: utf-8 -*-

import json
import time
import re
import os
import pickle
from django.http import HttpResponse
from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render_to_response
from django.core import serializers
from salts.models import Scenario, Shooting, Tank, TestResult
from django.contrib.auth.models import User, Group
from django.db.models import Max
from salts_prj.settings import log, LOCK_PATH
from salts_prj.requesthelper import (request_get_value, generate_context,
                                     add_version)
from salts_prj.ini import ini_manager, IniCtrlWarning
from tank_api_client import jsonstr2bin, bin2jsonstr
from salts.tankmanager import remainedtime
from salts_prj.celery import obtain_active_tanks, obtain_connection_time


SCENARIO_RPS_DEFAULT = 1


def duration2ms(line):
    line = line.replace(" ", "")
    ts = [("h", 3600000), ("m", 60000),
          ("s", 1000), ("ms", 1), ("", 1000)]
    total = 0
    for (unit, ms) in ts:
        regex = unit
        if unit == "m":
            regex = "m([^s]|$)"
        pat = re.compile("^(\d+){regex}".format(regex=regex))
        m = pat.match(line)
        if not m:
            continue
        if not unit and total:
            break
        value = m.groups()[0]
        total += ms * int(value)
        line = line.replace("{value}{unit}".format(value=value, unit=unit),
                            "", 1)
    return total


def phantom_rps_schedule(scenario_path):
    def parse_phantom_schedule(rps_line):
        steps = []
        for step in " ".join(rps_line.split("\n")).split(")"):
            line = step.strip()
            if not line:
                continue
            (name, params) = line.split("(")
            keys = {"step": ["a", "b", "step", "dur"],
                    "line": ["a", "b", "dur"],
                    "const": ["a", "dur"]}
            if name not in keys:
                params = {"load_gen": "phantom", "scenario_path": scenario_path}
                raise IniCtrlWarning("incorrect_rps_schedule", params)
            params = dict(zip(keys[name], params.split(",")))
            params["dur"] = duration2ms(params["dur"])
            steps.append({"loadtype": name, "params": params})
        return steps

    test_name = ini_manager.get_option_value(scenario_path,
                                             "sputnikreport",
                                             "test_name")
    if not test_name:
        params = {"scenario_path": scenario_path}
        raise IniCtrlWarning("no_test_name", params)
    dd = {"test_name": test_name}
    rps_line = ini_manager.get_option_value(scenario_path, "phantom",
                                            "rps_schedule")
    dd["steps"] = parse_phantom_schedule(rps_line)
    return dd


def phantom_target_info(scenario_path):
    addr = {"hostname": "", "port": 8000}
    target_info = ini_manager.get_option_value(scenario_path,
                                               "phantom", "address", "")
    if target_info:
        targ = target_info.split(":")
        addr["hostname"] = targ[0]
        if len(targ) >= 2:
            addr["port"] = targ[1]
    if not addr["hostname"]:
        params = {"load_gen": "phantom", "scenario_path": scenario_path}
        raise IniCtrlWarning("undefined_target", params)
    return addr


def jmeter_rps_schedule(scenario_path):
    def jmeter_duration(key):
        value = ini_manager.get_option_value(scenario_path, "jmeter", key)
        if not value:
            params = {"scenario_path": scenario_path, "key": key}
            raise IniCtrlWarning("undefined_duration", params)
        return 1000 * int(value)
    try:
        value = ini_manager.get_option_value(scenario_path, "jmeter",
                                             "rps1", SCENARIO_RPS_DEFAULT)
        rps = int(value)
        test_name = ini_manager.get_option_value(scenario_path, "sputnikreport",
                                                 "test_name")
        if not test_name:
            params = {"scenario_path": scenario_path}
            raise IniCtrlWarning("no_test_name", params)
        return {"test_name": test_name,
                "steps": [{"loadtype": "line",
                           "params": {"a": 1, "b": rps,
                                      "dur": jmeter_duration("rampup")}},
                          {"loadtype": "const",
                           "params": {"a": rps,
                                      "dur": jmeter_duration("testlen")}},
                          {"loadtype": "line",
                           "params": {"a": rps, "b": 1,
                                      "dur": jmeter_duration("rampdown")}}]}
    except ValueError:
        params = {"load_gen": "jmeter", "scenario_path": scenario_path}
        raise IniCtrlWarning("incorrect_rps_schedule", params)


def jmeter_target_info(scenario_path):
    addr = {"hostname": "", "port": 8000, "s": ""}
    target_info = ini_manager.get_option_value(scenario_path,
                                               "jmeter", "hostname", "")
    if target_info:
        targ = target_info.split(":")
        addr["hostname"] = targ[0]
        if len(targ) == 1:
            addr["port"] = ini_manager.get_option_value(scenario_path,
                                                        "jmeter", "port",
                                                        addr["port"])
            addr["s"] = "1"  # target и port д.б. сохранены в разных опциях
        else:
            addr["port"] = targ[1]
    if not addr["hostname"]:
        params = {"load_gen": "jmeter", "scenario_path": scenario_path}
        raise IniCtrlWarning("undefined_target", params)
    return addr


class ScenarioRunView(View):

    MAX_TESTRUN_DURATION = 60*60*24

    def __init__(self, *args, **kwargs):
        super(ScenarioRunView, self).__init__(*args, **kwargs)
        self._default_data = {}
        self._salts_group = Group.objects.get(name="Salts")
        self._actual_tanks_info = {}
        self._lock_dir_path = LOCK_PATH
        if not os.path.exists(self._lock_dir_path):
            os.mkdir(self._lock_dir_path)
        self._active_tanks_path = os.path.join(self._lock_dir_path, "tanks")
        self._tanks_lock_path = "%s.lock" % self._active_tanks_path
        self._tanks_mq_path = "%s.mq" % self._tanks_lock_path
        if not os.path.exists(self._tanks_lock_path) and \
           not os.path.exists(self._active_tanks_path):
            open(self._active_tanks_path, "w").close()

    @method_decorator(never_cache)
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ScenarioRunView, self).dispatch(*args, **kwargs)

    def get(self, request):
        response = None
        if request_get_value(request, 'a'):
            response = self.get_test_status(request)
        else:
            context = generate_context(request)
            response = render_to_response('run_test.html', context)
        add_version(response)
        return response

    def active_shootings(self):
        shootings = Shooting.objects.filter(status='R')
        invalid = []
        for s in shootings:
            current_time = time.time()
            planned_finish = 0
            if not s.start:
                log.warning("The active shooting (id=%s) is invalid: "
                            "start time is unknown" % s.id)
                invalid.append(s.id)
                continue
            if s.planned_duration:
                planned_finish = s.start + s.planned_duration
            else:
                planned_finish = s.start + ScenarioRunView.MAX_TESTRUN_DURATION
            if current_time > planned_finish:
                log.warning("Likely the shooting (id=%s) is not running "
                            "at this time, but its status is 'Running'."
                            % s.id)
                invalid.append(s.id)
        return shootings.exclude(id__in=invalid)

    def get_active_tanks(self, http_host):
        while True:
            if not os.path.exists(self._tanks_lock_path):
                os.rename(self._active_tanks_path,
                          self._tanks_lock_path)
                break
        if os.path.exists(self._tanks_mq_path):
            os.rename(self._tanks_mq_path, self._tanks_lock_path)
        tanks = Tank.objects.all()
        s = os.stat(self._tanks_lock_path)
        cr_date = os.path.getmtime(self._tanks_lock_path)
        ctime = time.time()
        if ctime - cr_date > 30 or s.st_size == 0:
            jtanks = json.loads(serializers.serialize("json", tanks))
            obtain_active_tanks.delay(self._tanks_mq_path, jtanks, http_host)
        if s.st_size:
            with open(self._tanks_lock_path, "rb") as f:
                active_id = pickle.load(f)
                tanks = tanks.filter(id__in=active_id)
        else:
            tanks = []
        jtanks = json.loads(serializers.serialize("json", tanks))
        os.rename(self._tanks_lock_path, self._active_tanks_path)
        return jtanks

    def get_default_data(self, scenario_path):
        if scenario_path in self._default_data:
            return self._default_data[scenario_path]
        self._default_data[scenario_path] = {}
        try:
            scenario_type = ini_manager.scenario_type(scenario_path)
            ini_manager.get_rps_sections(scenario_path)
            rps_schedule = {"phantom": phantom_rps_schedule,
                            "jmeter": jmeter_rps_schedule}
            target_info = {"phantom": phantom_target_info,
                           "jmeter": jmeter_target_info}
            dd = rps_schedule[scenario_type](scenario_path)
            dd.update(target_info[scenario_type](scenario_path))
        except IniCtrlWarning, exc:
            return {"error": {"name": exc.name, "params": exc.params}}
        dd["gen_type"] = scenario_type
        self._default_data[scenario_path] = dd
        return dd

    def adapt_tanks_list(self, tanks_list, active_shootings, request_user):
        if request_user.id in self._actual_tanks_info:
            for record in self._actual_tanks_info[request_user.id]:
                sh = active_shootings.filter(id=record["shooting"]["id"])
                if sh:
                    record["shooting"]["remained"] = remainedtime(sh[0])
                else:
                    self._actual_tanks_info[request_user.id]["shooting"] = {}
        else:
            self._actual_tanks_info[request_user.id] = []
            for tank in tanks_list:
                rec = {"value": tank["pk"],
                       "text": tank["fields"]["host"],
                       "shooting": {}}
                sh = active_shootings.filter(tank_id=tank["pk"])
                if sh:
                    if len(sh) > 1:
                        log.warning("There are more than 1 active shooting "
                                    "on the tank host")
                    shooting = sh[0]
                    default_data = \
                        self.get_default_data(shooting.scenario.scenario_path)
                    can_stop = request_user.id == shooting.user.id or \
                        self._salts_group in request_user.groups.all()
                    rec["shooting"] = {"id": shooting.id,
                                       "session": shooting.session_id,
                                       "start": shooting.start,
                                       "remained": remainedtime(shooting),
                                       "scenario_id": shooting.scenario_id,
                                       "username": shooting.user.username,
                                       "default_data": default_data,
                                       "custom_data": jsonstr2bin(
                                           str(shooting.custom_data)),
                                       "can_stop": can_stop}
                self._actual_tanks_info[request_user.id].append(rec)
            # records.append(json.dumps(rec))
        return [json.dumps(r)
                for r in self._actual_tanks_info[request_user.id]]

    def select_tank_host(self, tanks, active_shootings, trg_host, trg_port,
                         scenario_path):
        ct_fname = "%s_%s" % (trg_host.replace(".", "_"),
                              trg_port)
        ct_fpath = os.path.join(self._lock_dir_path,
                                ct_fname)
        ct_fpath_lock = "%s.lock" % ct_fpath
        trg_host_parts = trg_host.split(".")
        sfx = ""
        if len(trg_host_parts) > 1:
            sfx = ".%s" % ".".join(trg_host_parts[1:])
        extanks = {t["fields"]["host"]: t["pk"] for t in tanks}
        tank_set = set([t["fields"]["host"] for t in tanks
                        if t["fields"]["host"].endswith(
                                sfx) or t["fields"]["host"].endswith(
                                            ".int.pv.km")])
        if not tank_set:
            tank_set = set([t["fields"]["host"] for t in tanks])
        while True:
            if not os.path.exists(ct_fpath_lock):
                if not os.path.exists(ct_fpath):
                    open(ct_fpath, "w").close()
                os.rename(ct_fpath, ct_fpath_lock)
                break
        ct_fpath_lock_mq = "%s.mq" % ct_fpath_lock
        if os.path.exists(ct_fpath_lock_mq):
            os.rename(ct_fpath_lock_mq, ct_fpath_lock)
        s = os.stat(ct_fpath_lock)
        ctimes = {}
        current_id = ""
        if s.st_size:
            with open(ct_fpath_lock, "rb") as f:
                (current_id, ctimes) = pickle.load(f)
        cr_date = os.path.getmtime(ct_fpath_lock)
        ctime = time.time()
        need_upd = (ctime - cr_date > 30) or (not s.st_size)
        if need_upd and (not current_id) and tank_set:
            current_id = obtain_connection_time.delay(ct_fpath_lock_mq,
                                                      ",".join(tank_set),
                                                      trg_host, trg_port)
            with open(ct_fpath_lock, "wb") as f:
                pickle.dump((current_id, ctimes), f)
        tank_host = ""
        ctimes = None
        if s.st_size:
            with open(ct_fpath_lock, "rb") as f:
                (current_id, ctimes) = pickle.load(f)
                if ctimes:
                    from collections import OrderedDict
                    ord_ctimes = OrderedDict(sorted(ctimes.items(),
                                                    key=lambda t: t[1]))
                    for host_name in ord_ctimes:
                        if host_name not in extanks:
                            continue
                        tank_id = extanks.get(host_name)
                        if not active_shootings.filter(tank_id=tank_id):
                            tank_host = host_name
                            break
        os.rename(ct_fpath_lock, ct_fpath)
        if not ctimes:
            params = {"host": trg_host, "port": trg_port,
                      "scenario_path": scenario_path}
            raise IniCtrlWarning("inaccessible_target", params)
        if not tank_host:
            params = {"scenario_path": scenario_path}
            raise IniCtrlWarning("no_free_tank", params)
        return {"id": extanks[tank_host], "name": tank_host}

    def get_test_status(self, request):
        b_value = request_get_value(request, 'b')
        scen_ids = []
        if b_value:
            jsonstr = bin2jsonstr(b_value)
            scen_ids = json.loads(jsonstr)
        scenarios = Scenario.objects.filter(
                        group_id__in=User.objects.get(
                                        id=request.user.id).groups.all(),
                        status='A')
        if scen_ids:
            scenarios = scenarios.filter(id__in=scen_ids)
        sh = Shooting.objects.filter(scenario_id__in=scenarios.values('id'))
        sh_max = sh.values('scenario_id').annotate(max_finish=Max('finish'))
        tr = TestResult.objects.filter(
                scenario_path__in=scenarios.values('scenario_path'))
        tr_max = tr.values('scenario_path').annotate(
                                                max_finish=Max('dt_finish'))
        active_sh = self.active_shootings()
        sort = request_get_value(request, "sort")
        if sort:
            order = request_get_value(request, "order")
            reverse = ""
            if not order:
                order = "asc"
            if order == "desc":
                reverse = "-"
            scenarios = scenarios.order_by("%sid" % reverse)
        response_dict = {}
        response_dict["total"] = len(scenarios)
        offset = request_get_value(request, "offset")
        limit = request_get_value(request, "limit")
        if offset and limit:
            offset = int(offset)
            limit = int(limit)
            scenarios = scenarios[offset:offset+limit]

        results = []
        tanks = self.get_active_tanks(request.META["HTTP_HOST"])
        for s in scenarios:
            values = {}
            values["id"] = s.id
            values["test_name"] = ini_manager.get_scenario_name(s.scenario_path)
            values["default_data"] = self.get_default_data(s.scenario_path)
            values["tank_host"] = {"id": "-1", "name": ""}
            if "error" not in values["default_data"]:
                try:
                    values["tank_host"] = self.select_tank_host(
                                            tanks, active_sh,
                                            values["default_data"]["hostname"],
                                            values["default_data"]["port"],
                                            s.scenario_path)
                    values["last"] = {}
                    shs = sh_max.filter(scenario_id=s.id)
                    trs = tr_max.filter(scenario_path=s.scenario_path)
                    if shs and trs:
                        trs = TestResult.objects.filter(
                                scenario_path=s.scenario_path,
                                dt_finish=trs[0]["max_finish"])
                        values["last"] = {"tr_id": trs[0].id,
                                          "finish": shs[0]["max_finish"]}
                except IniCtrlWarning, exc:
                    values["default_data"]["error"] = {"name": exc.name,
                                                       "params": exc.params}
            results.append(values)
        response_dict["rows"] = results
        response_dict["tanks"] = self.adapt_tanks_list(tanks, active_sh,
                                                       request.user)
        response = HttpResponse(json.dumps(response_dict),
                                content_type="application/json")
        return response
