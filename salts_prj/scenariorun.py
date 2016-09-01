# -*- coding: utf-8 -*-

import json
import time
from operator import itemgetter
from django.http import HttpResponse
from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render_to_response
from django.db import connection
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

    def get_test_status(self, request):
        cursor = connection.cursor()
        cursor.execute(
            """
                SELECT ss.id, ss.scenario_path FROM salts_scenario ss
                JOIN auth_user_groups usr_gr USING(group_id)
                WHERE usr_gr.user_id = '{user_id}'
            """.format(user_id=request.user.id))
        tanks = Tank.objects.all()
        shootings = self.active_shootings()
        log.info("Active Shootings Len: %s" % len(shootings))
        results = []
        for record in cursor.fetchall():
            values = {}
            (values['id'], scenario_path) = record
            values['test_name'] = ini_manager.get_scenario_name(scenario_path)
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
        response_dict['rows'] = results
        response = HttpResponse(json.dumps(response_dict),
                                content_type='application/json')
        return response
