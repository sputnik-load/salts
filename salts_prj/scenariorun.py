# -*- coding: utf-8 -*-

import json
import time
import copy
import re
from operator import itemgetter
from django.http import HttpResponse
from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render_to_response
from django.db import connection
from django.core import serializers
from salts.models import Scenario, Shooting, Tank, TestResult
from django.contrib.auth.models import User, Group
from django.db.models import Max
from salts_prj.settings import log
from salts_prj.requesthelper import (request_get_value, generate_context,
                                     add_version)
from salts_prj.ini import ini_manager
from tank_api_client import jsonstr2bin, bin2jsonstr
from salts.tankmanager import remainedtime


SCENARIO_RPS_DEFAULT = '2'
SCENARIO_DURATIONS_DEFAULT = {'rampup': '5000',
                              'testlen': '90000',
                              'rampdown': '5000'
                             }


def duration2ms(line):
    ts = [('h', 3600000), ('m[^s]', 60000),
          ('s', 1000), ('ms', 1), ('', 1000)]
    total = 0
    for (unit, ms) in ts:
        pat = re.compile("^(\d+)%s" % unit)
        m = pat.match(line)
        if not m:
            continue
        if not unit and total:
            break
        total += ms * int(m.groups()[0])
        line = pat.sub('', line)
    return total


def phantom_rps_schedule(scenario_path):
    dd = {'test_name': ini_manager.get_option_value(scenario_path,
                                                    'sputnikreport',
                                                    'test_name')
         }
    sample = ['line', 'const', 'line']
    rps_line = ini_manager.get_option_value(scenario_path, 'phantom',
                                            'rps_schedule')
    rps_line = re.sub('\n|\t| ', '', rps_line)
    pat = re.compile("(line|const|step)\(.*?\)")
    m = pat.findall(rps_line)
    rps = 0
    durs = {}
    valid = m == sample
    if valid:
        pat = re.compile("^line\((\d+),(\d+),(.*?)\).*")
        m = pat.findall(rps_line)
        valid = m and len(m[0]) == 3 and m[0][0] == '1'
        if valid:
            rps = m[0][1]
            durs['rampup'] = duration2ms(m[0][2])
        if valid:
            pat = re.compile(".*const\((\d+),(.*?)\).*")
            m = pat.findall(rps_line)
            valid = m and len(m[0]) == 2 and m[0][0] == rps
            if valid:
                durs['testlen'] = duration2ms(m[0][1])
                pat = re.compile(".*line\((\d+),(\d+),(.*?)\)$")
                m = pat.findall(rps_line)
                valid = m and len(m[0]) == 3 and m[0][0] == rps and m[0][1] == '1'
                if valid:
                    durs['rampdown'] = duration2ms(m[0][2])
    if valid:
        log.info("Phantom Durations (ms): %s" % durs)
        dd.update({'rps': rps})
        dd.update(durs)
        return dd
    else:
        log.info("RPS Schedule will be replaced with default.")
        dd.update({'rps': SCENARIO_RPS_DEFAULT})
        dd.update(SCENARIO_DURATIONS_DEFAULT)
        return dd


def phantom_target_info(scenario_path):
    result = {'target': '', 'port': 8000}
    target_info = ini_manager.get_option_value(scenario_path, 'phantom', 'address', '')
    if not target_info:
        return  result
    targ = target_info.split(':')
    if len(targ) >= 2:
        return {'target': targ[0], 'port': targ[1]}
    return {'target': targ[0], 'port': def_values['port']}


def jmeter_rps_schedule(scenario_path):
    def jmeter_duration(key):
        return str(1000 * int(ini_manager.get_option_value(scenario_path, 'jmeter', key,
                                int(SCENARIO_DURATIONS_DEFAULT[key]) / 1000)))
    return {'test_name': ini_manager.get_option_value(scenario_path,
                                                       'sputnikreport',
                                                       'test_name'),
            'rampup': jmeter_duration('rampup'),
            'testlen': jmeter_duration('testlen'),
            'rampdown': jmeter_duration('rampdown'),
            'rps': ini_manager.get_option_value(scenario_path, 'jmeter', 'rps1',
                                                SCENARIO_RPS_DEFAULT)
           }


def jmeter_target_info(scenario_path):
    result = {'target': '', 'port': 8000,
              's': ''}
    target_info = ini_manager.get_option_value(scenario_path,
                                               'jmeter', 'hostname', '')
    if target_info:
        targ = target_info.split(':')
        result['target'] = targ[0]
        if len(targ) == 1:
            result['port'] = ini_manager.get_option_value(scenario_path,
                                                          'jmeter', 'port',
                                                          result['port'])
            result['s'] = '1' # target и port д.б.
                              # сохранены в разных опциях
        else:
            result['port'] = targ[1]
    return result


class ScenarioRunView(View):

    MAX_TESTRUN_DURATION=60*60*24

    def __init__(self, *args, **kwargs):
        super(ScenarioRunView, self).__init__(*args, **kwargs)
        self._default_data = {}
        self._salts_group = Group.objects.get(name="Salts")
        self._actual_tanks_info = {}

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
                log.warning("Likely the shooting (id=%s) is not running " \
                            "at this time, but its status is 'Running'." \
                            % s.id)
                invalid.append(s.id)
        return shootings.exclude(id__in=invalid)

    def get_default_data(self, scenario_path):
        log.info("testing1372: get_default_data: scenario_path: %s",
                 scenario_path)
        if scenario_path in self._default_data:
            return self._default_data[scenario_path]
        self._default_data[scenario_path] = {}
        rps_default_section = ini_manager.scenario_type(scenario_path)
        if not rps_default_section:
            return {}
        if rps_default_section not in ini_manager.get_rps_sections(scenario_path):
            log.warning("'%s' section is required." % rps_default_section)
            return {}
        rps_schedule = {'phantom': phantom_rps_schedule,
                        'jmeter': jmeter_rps_schedule}
        target_info = {'phantom': phantom_target_info,
                       'jmeter': jmeter_target_info}
        dd = rps_schedule[rps_default_section](scenario_path)
        dd['gen_type'] = rps_default_section
        dd.update(target_info[rps_default_section](scenario_path))
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
                                       "custom_data": jsonstr2bin(str(shooting.custom_data)),
                                       "can_stop": can_stop
                                    }
                self._actual_tanks_info[request_user.id].append(rec)
            # records.append(json.dumps(rec))
        return [json.dumps(r)
                for r in self._actual_tanks_info[request_user.id]]

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
        tanks = json.loads(serializers.serialize('json',
                                                 Tank.objects.all()))
        for s in scenarios:
            values = {}
            values['id'] = s.id
            values['test_name'] = ini_manager.get_scenario_name(s.scenario_path)
            values['default_data'] = self.get_default_data(s.scenario_path)
            values['last'] = {}
            shs = sh_max.filter(scenario_id=s.id)
            trs = tr_max.filter(scenario_path=s.scenario_path)
            if shs and trs:
                trs = TestResult.objects.filter(
                        scenario_path=s.scenario_path,
                        dt_finish=trs[0]['max_finish'])
                values['last'] = {'tr_id': trs[0].id,
                                  'finish': shs[0]['max_finish']}
            results.append(values)
        response_dict['rows'] = results
        response_dict['tanks'] = self.adapt_tanks_list(tanks, active_sh,
                                                       request.user)
        response = HttpResponse(json.dumps(response_dict),
                                content_type='application/json')
        return response
