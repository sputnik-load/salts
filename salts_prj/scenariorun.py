# -*- coding: utf-8 -*-

import json
import time
import copy
from operator import itemgetter
from django.http import HttpResponse
from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render_to_response
from django.db import connection
from django.core import serializers
from salts.models import Scenario, Shooting, Tank
from django.contrib.auth.models import User
from salts_prj.settings import log
from salts_prj.requesthelper import (request_get_value, generate_context,
                                     add_version)
from salts_prj.ini import ini_manager


class ScenarioRunView(View):

    MAX_TESTRUN_DURATION=60*60*24

    def __init__(self, *args, **kwargs):
        super(ScenarioRunView, self).__init__(*args, **kwargs)

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
        dd = {'sputnikreport':
                {'test_name': ini_manager.get_option_value(scenario_path,
                                                           'sputnikreport',
                                                           'test_name')
                }
             }
        gentype = ini_manager.scenario_type(scenario_path)
        if gentype == 'phantom':
            dd['phantom'] = {
                'rps_schedule': ini_manager.get_option_value(scenario_path,
                                                             'phantom',
                                                             'rps_schedule')}
        if gentype == 'jmeter':
            dd['jmeter'] = {
                'rampup': ini_manager.get_option_value(scenario_path,
                                                       'jmeter',
                                                       'rampup'),
                'testlen': ini_manager.get_option_value(scenario_path,
                                                        'jmeter',
                                                        'testlen'),
                'rampdown': ini_manager.get_option_value(scenario_path,
                                                         'jmeter',
                                                         'rampdown'),
            }
        return dd

    def adapt_tanks_list(self, tanks_list, active_shootings):
        records = []
        for tank in tanks_list:
            rec = {'value': tank['pk'],
                   'text': tank['fields']['host'],
                   'shooting': {}}
            sh = active_shootings.filter(tank_id=tank['pk'])
            if sh:
                if len(sh) > 1:
                    log.warning("There are more than 1 active shooting "
                                "on the tank host");
                shooting = sh[0]
                default_data = \
                    self.get_default_data(shooting.scenario.scenario_path)
                rec['shooting'] = {'id': shooting.id,
                                   'scenario_id': shooting.scenario_id,
                                   'default_data': default_data,
                                   'custom_data': shooting.custom_data}
            records.append(json.dumps(rec))
        return records

    def get_test_status(self, request):
        cursor = connection.cursor()
        cursor.execute(
            """
                SELECT ss.id, ss.scenario_path FROM salts_scenario ss
                JOIN auth_user_groups usr_gr USING(group_id)
                WHERE usr_gr.user_id = {user_id} AND ss.status = 'A'
            """.format(user_id=request.user.id))
        shootings = self.active_shootings()
        results = []
        tanks = json.loads(serializers.serialize('json',
                                                 Tank.objects.all()))
        for record in cursor.fetchall():
            tanks_list = copy.copy(tanks)
            values = {'tank_host': '[]'}
            (scenario_id, scenario_path) = record
            values['id'] = scenario_id
            values['test_name'] = ini_manager.get_scenario_name(scenario_path)
            values['default_data'] = self.get_default_data(scenario_path)
            results.append(values)
        sort = request_get_value(request, 'sort')
        if sort:
            order = request_get_value(request, 'order')
            if not order:
                order = 'asc'
            reverse = order == 'desc'
            results = sorted(results, key=itemgetter('id'), reverse=reverse)

        response_dict = {}
        response_dict['total'] = len(results)
        offset = request_get_value(request, 'offset')
        limit = request_get_value(request, 'limit')
        if offset and limit:
            offset = int(offset)
            limit = int(limit)
            results = results[offset:offset+limit]
        response_dict['rows'] = results
        response_dict['tanks'] = self.adapt_tanks_list(tanks, shootings)
        response = HttpResponse(json.dumps(response_dict),
                                content_type='application/json')
        return response
