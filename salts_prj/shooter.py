# -*- coding: utf-8 -*-

import time
import json
from urllib import unquote_plus
from django.http import HttpResponse
from django.views.generic import View
from django.contrib.auth.models import User
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
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
            return self.stop_shooting(shooting_id)

        scenario_id = request_get_value(request, 'scid')
        tank_host = request_get_value(request, 'tank_host')
        custom_data = request_get_value(request, 'custom_data')
        return self.start_shooting(scenario_id, tank_host, custom_data,
                                   request.user)

    def start_shooting(self, scenario_id, tank_host, custom_data, user):
        json_str = '{}'
        if custom_data:
            b64line = unquote_plus(custom_data)
            json_str = b64line.decode('base64', 'strict')
        config = json.loads(json_str)
        if 'salts' not in config:
            config['salts'] = {}
        if 'api_user' not in config['salts']:
            config['salts']['api_user'] = user.username
        if 'api_key' not in config['salts']:
            user = User.objects.get(username=config['salts']['api_user'])
            tokens = Token.objects.filter(user_id=user.id)
            config['salts']['api_key'] = tokens[0].key
        log.info("Scenario ID: %s" % scenario_id)
        scenario = Scenario.objects.get(id=scenario_id)
        tank = Tank.objects.get(host=tank_host)
        start_shooting_process(scenario=scenario, tank=tank,
                               custom_data=json.dumps(config))
        response_dict = {}
        while True:
            log.info("Wait for shooting start.")
            time.sleep(1)
            shootings = Shooting.objects.order_by('-id')
            if shootings:
                sh = shootings[0]
                if sh.status == 'R':
                    response_dict['id'] = sh.id
                    break
        return HttpResponse(json.dumps(response_dict),
                            content_type="application/json")

    def stop_shooting(self, id):
        shooting = Shooting.objects.get(id=id)
        tank_manager.interrupt(shooting)
        while True:
            time.sleep(1)
            shooting = Shooting.objects.get(id=id)
            if shooting.finish:
                shooting.status = 'I'
                shooting.save()
                break
        response_dict = {}
        response_dict['stopped'] = True
        return HttpResponse(json.dumps(response_dict),
                            content_type="application/json")
