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


def request_get_value(request, param):
    value = None
    if param in request.GET:
        value = request.GET[param]
    return value


@postpone
def start_shooting_process(**kwargs):
    log.info("testing3100: start shooting process.")
    tank_manager.shoot(**kwargs)


class ShooterView(View):

    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(ShooterView, self).dispatch(*args, **kwargs)

    def get(self, request):
        custom_data = request_get_value(request, 'custom_data')
        json_str = '{}'
        if custom_data:
            b64line = unquote_plus(custom_data)
            json_str = b64line.decode('base64', 'strict')
        config = json.loads(json_str)
        if 'salts' not in config:
            config['salts'] = {}
        if 'api_user' not in config['salts']:
            config['salts']['api_user'] = request.user.username
        if 'api_key' not in config['salts']:
            user = User.objects.get(username=config['salts']['api_user'])
            tokens = Token.objects.filter(user_id=user.id)
            config['salts']['api_key'] = tokens[0].key
        tank_host = request_get_value(request, 'tank_host')
        scenario_id = request_get_value(request, 'scid')
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
                    response_dict['start_time'] = sh.start
                    response_dict['id'] = sh.id
                    break
        return HttpResponse(json.dumps(response_dict),
                            content_type="application/json")
