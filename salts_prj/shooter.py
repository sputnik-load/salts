# -*- coding: utf-8 -*-

import time
import json
from urllib import unquote_plus
from django.http import HttpResponse
from django.views.generic import View
from django.contrib.auth.models import User
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.db import connection
from salts.models import Scenario, Tank, Shooting
from salts.tankmanager import tank_manager
from salts_prj.settings import log
from rest_framework.authtoken.models import Token
from salts_prj.tasks import postpone
from requesthelper import request_get_value


@postpone
def start_shooting_process(**kwargs):
    tank_manager.shoot(**kwargs)


class ShooterView(View):

    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(ShooterView, self).dispatch(*args, **kwargs)

    def get(self, request):
        shooting_id = request_get_value(request, 'stop')
        if shooting_id:
            return self.stop_shooting(shooting_id, request.user.username)

        scenario_id = request_get_value(request, 's')
        tank_id = request_get_value(request, 't')
        custom_data = request_get_value(request, 'j')
        return self.start_shooting(scenario_id, tank_id, custom_data,
                                   request.user.username)

    def have_perm_start(self, username, scenario_id):
        cursor = connection.cursor()
        cursor.execute(
            """
                SELECT usr_gr.id FROM auth_user usr
                JOIN auth_user_groups usr_gr ON usr.id = usr_gr.user_id
                JOIN salts_scenario ss USING(group_id)
                WHERE ss.id = {scenario_id} and usr.username = '{username}'
            """.format(scenario_id=scenario_id, username=username))
        return bool(cursor.fetchone())

    def have_perm_stop(self, username, shooting_id):
        cursor = connection.cursor()
        cursor.execute(
            """
                SELECT sh.id FROM salts_shooting sh
                JOIN auth_user_groups usr_gr USING(user_id)
                JOIN auth_user_groups usr_gr_req
                    ON usr_gr_req.group_id=usr_gr.group_id
                JOIN auth_user usr_req ON usr_req.id=usr_gr_req.user_id
                WHERE sh.id={shooting_id} AND usr_req.username='{req_username}'
            """.format(shooting_id=shooting_id, req_username=username))
        return bool(cursor.fetchone())


    def start_shooting(self, scenario_id, tank_id, custom_data, username):
        response_dict = {'message': ''}
        try:
            scenario = Scenario.objects.get(id=scenario_id)
        except Scenario.DoesNotExist:
            response_dict['status'] = 'failed'
            response_dict['message'] = "Given scenario_id=%s isn't valid." \
                                       % scenario_id
            log.warning(response_dict['message'])
            return HttpResponse(json.dumps(response_dict),
                                content_type="application/json",
                                status=401)
        try:
            tank = Tank.objects.get(id=tank_id)
        except Tank.DoesNotExist:
            response_dict['status'] = 'failed'
            response_dict['message'] = "Given tank_id=%s isn't valid." \
                                       % tank_id
            log.warning(response_dict['message'])
            return HttpResponse(json.dumps(response_dict),
                                content_type="application/json",
                                status=401)
        json_str = '{}'
        if custom_data:
            b64line = unquote_plus(custom_data)
            json_str = b64line.decode('base64', 'strict')
        config = json.loads(json_str)
        if 'salts' not in config:
            config['salts'] = {}
        if 'api_user' not in config['salts']:
            if username:
                config['salts']['api_user'] = username
            else:
                response_dict['status'] = 'failed'
                response_dict['message'] = "User isn't authenticated " \
                                           "or api_user option isn't provided."
                log.warning(response_dict['message'])
                return HttpResponse(json.dumps(response_dict),
                                    content_type="application/json",
                                    status=401)

        if not self.have_perm_start(config['salts']['api_user'], scenario_id):
            response_dict = {}
            response_dict['status'] = 'failed'
            response_dict['message'] = "Test %s disabled for '%s' user." \
                                       % (scenario.scenario_path,
                                          config['salts']['api_user'])
            log.warning(response_dict['message'])
            return HttpResponse(json.dumps(response_dict),
                                content_type="application/json",
                                status=403)

        if 'api_key' not in config['salts']:
            user = User.objects.get(username=config['salts']['api_user'])
            tokens = Token.objects.filter(user_id=user.id)
            config['salts']['api_key'] = tokens[0].key
        start_shooting_process(scenario=scenario, tank=tank,
                               custom_data=json.dumps(config))
        while True:
            log.info("Wait for shooting start.")
            time.sleep(1)
            shootings = Shooting.objects.order_by('-id')
            if shootings:
                sh = shootings[0]
                if sh.status == 'R':
                    response_dict['id'] = sh.id
                    response_dict['status'] = 'success'
                    break
        return HttpResponse(json.dumps(response_dict),
                            content_type="application/json")

    def stop_shooting(self, shooting_id, username):
        if not self.have_perm_stop(username, shooting_id):
            response_dict = {}
            response_dict['status'] = 'failed'
            response_dict['message'] = \
                "Shooting cannot be stopped by '%s' user." % username
            log.warning(response_dict['message'])
            return HttpResponse(json.dumps(response_dict),
                                content_type="application/json",
                                status=403)

        shooting = Shooting.objects.get(id=shooting_id)
        tank_manager.interrupt(shooting)
        while True:
            time.sleep(1)
            shooting = Shooting.objects.get(id=shooting_id)
            if shooting.finish:
                shooting.status = 'I'
                shooting.save()
                break
        response_dict = {}
        response_dict['stopped'] = True
        return HttpResponse(json.dumps(response_dict),
                            content_type="application/json")
