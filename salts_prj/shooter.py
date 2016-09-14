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
from salts_prj.tasks import postpone, errors
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

    def check_perm_start(self, config, reqdata):
        username = config['salts']['api_user']
        scenario = reqdata['scenario']
        cursor = connection.cursor()
        cursor.execute(
            """
                SELECT usr_gr.id FROM auth_user usr
                JOIN auth_user_groups usr_gr ON usr.id = usr_gr.user_id
                JOIN salts_scenario ss USING(group_id)
                WHERE ss.id = {scenario_id} and usr.username = '{username}'
            """.format(scenario_id=scenario.id, username=username))
        if cursor.fetchone():
            return None
        resp = {'status': 'failed',
                'message': "Test %s disabled for '%s' user." \
                           % (scenario.scenario_path,
                              config['salts']['api_user'])}
        log.warning(resp['message'])
        return HttpResponse(json.dumps(resp),
                            content_type="application/json",
                            status=403)

    def obtain_scenario(self, scenario_id, reqdata):
        try:
            reqdata['scenario'] = Scenario.objects.get(id=scenario_id)
            return None
        except Scenario.DoesNotExist:
            resp = {'status': 'failed',
                    'message': "Given scenario_id=%s isn't valid." \
                               % scenario_id}
            log.warning(resp['message'])
            return HttpResponse(json.dumps(resp),
                                content_type="application/json",
                                status=404)

    def obtain_tank(self, tank_id, reqdata):
        try:
            reqdata['tank'] = Tank.objects.get(id=tank_id)
            return None
        except Tank.DoesNotExist:
            resp = {'status': 'failed',
                    'message': "Given tank_id=%s isn't valid." \
                               % tank_id}
            log.warning(resp['message'])
            return HttpResponse(json.dumps(resp),
                                content_type="application/json",
                                status=404)

    def check_auth(self, username, config):
        if 'api_user' in config['salts']:
            return None
        if username:
            config['salts']['api_user'] = username
            return None
        resp = {'status': 'failed',
                'message': "User isn't authenticated " \
                            "or api_user option isn't provided."}
        log.warning(resp['message'])
        return HttpResponse(json.dumps(resp),
                            content_type="application/json",
                            status=401)

    def check_perm_stop(self, username, shooting_id):
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
        if cursor.fetchone():
            return None
        resp = {'status': 'failed',
                'message': "Shooting cannot be stopped by '%s' user." \
                           % username}
        log.warning(resp['message'])
        return HttpResponse(json.dumps(resp),
                            content_type="application/json",
                            status=403)

    def check_for_error(self, **kwargs):
        if errors['TankClient']:
            for err in errors['TankClient']:
                tank = kwargs['tank']
                if err['host'] == tank.host and err['port'] == tank.port:
                    resp = {'status': 'failed',
                            'message': err['message']}
                    log.warning(resp['message'])
                    return HttpResponse(json.dumps(resp),
                                        content_type="application/json",
                                        status=434)

    def save_custom_data(self, shooting, custom_data, custom_saved):
        if not custom_saved and shooting:
            shooting.custom_data = custom_data
            shooting.save()
            custom_saved = True
        return custom_saved

    def start_shooting(self, scenario_id, tank_id, custom_data, username):
        reqdata = {}
        err = self.obtain_scenario(scenario_id, reqdata)
        if err:
            return err
        err = self.obtain_tank(tank_id, reqdata)
        if err:
            return err
        json_str = '{}'
        if custom_data:
            b64line = unquote_plus(custom_data)
            json_str = b64line.decode('base64', 'strict')
        config = json.loads(json_str)
        if 'salts' not in config:
            config['salts'] = {}
        err = self.check_auth(username, config)
        if err:
            return err
        err = self.check_perm_start(config, reqdata)
        if err:
            return err

        if 'api_key' not in config['salts']:
            user = User.objects.get(username=config['salts']['api_user'])
            tokens = Token.objects.filter(user_id=user.id)
            config['salts']['api_key'] = tokens[0].key
        reqdata['custom_data'] = json.dumps(config)
        start_shooting_process(**reqdata)
        custom_saved = False
        session_id = None
        while True:
            shooting = None
            log.info("Wait for shooting start.")
            time.sleep(1)
            if not session_id:
                session_id = tank_manager.read_from_lock(tank_id,
                                                         'session_id')
            if session_id:
                shooting = Shooting.objects.get(session_id=session_id)

            custom_saved = self.save_custom_data(shooting,
                                                 reqdata['custom_data'],
                                                 custom_saved)
            if shooting and shooting.status == 'R':
                resp = {'status': 'success',
                        'id': shooting.id}
                return HttpResponse(json.dumps(resp),
                                    content_type="application/json")
            err_resp = self.check_for_error(**reqdata)
            if err_resp:
                self.save_custom_data(shooting, reqdata['custom_data'],
                                      custom_saved)
                return err_resp

    def stop_shooting(self, shooting_id, username):
        err = self.check_perm_stop(username, shooting_id)
        if err:
            return err

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
