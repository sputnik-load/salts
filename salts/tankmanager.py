# -*- coding: utf-8 -*-

import threading
import time
import os
from logger import Logger
from api_client import TankClient
from salts_prj.settings import LT_PATH


log = Logger.get_logger()


def stg_completed_to_bool(value):
    if type(value) is bool:
        return value

    return value.lower() == "true"


class TankManagerException(Exception):
    pass


class TankManager(object):

    POLL_INTERVAL = 5

    def __init__(self):
        self.tanks = {}
        self.lock = threading.Lock()

    def book(self, tank_id):
        self.lock.acquire()
        if self.is_busy(tank_id):
            return False
        self.tanks[tank_id] = {"is_busy": True}
        self.lock.release()
        return True

    def free(self, tank_id):
        self.lock.acquire()
        if tank_id in self.tanks:
            self.tanks[tank_id]["is_busy"] = False
        self.lock.release()
        return True

    def test_id(self, tank_id):
        if tank_id in self.tanks:
            return self.tanks[tank_id]["test_id"]
        return ""

    def is_busy(self, tank_id):
        if tank_id in self.tanks:
            return self.tanks[tank_id]["is_busy"]
        return False

    def start(self, instance):
        thread_data = {"instance": instance}
        t = threading.Thread(name="Shooting Id", target=self.shoot,
                             kwargs=thread_data)
        t.start()

    def _check_for_running(self, client):
        while True:
            resp = client.status()
            running = False
            for sess_id in resp:
                if resp[sess_id]["status"] == "running":
                    log.info("Test can't start because other test with id=%s is running now." % sess_id)
                    running = True
                    break
            if not running:
                break
            time.sleep(TankManager.POLL_INTERVAL)

    def _wait_for_completed(self, client, tank_id, expected_retcode):
        test_id = self.tanks[tank_id]["test_id"]
        while True:
            resp = client.status(test_id)
            if "stage_completed" in resp:
                status = resp["status"]
                completed = stg_completed_to_bool(resp["stage_completed"])
                if expected_retcode:
                    if resp["retcode"] is None:
                        completed = False
                if completed:
                    log.info("Test %s. Response: %s" % (status, resp))
                    break
                log.info("Test %s. Response: %s" % (status, resp))
            else:
                log.info("Response: %s" % resp)
            time.sleep(TankManager.POLL_INTERVAL)

    def shoot(self, **kwargs):
        log.info("Run Shooting: kwargs=%s" % kwargs)
        instance = kwargs["instance"]
        log.info("Shoot: host: %s, port: %s" % (instance.tank.host,
                                                instance.tank.port))
        client = TankClient(instance.tank.host, instance.tank.port)
        config_path = os.path.join(LT_PATH, instance.test_ini.scenario_id)
        log.info("Config Path: %s" % config_path)
        # self._check_for_running(client)
        resp = None
        with open(config_path) as ini_file:
            resp = client.run(ini_file.read(), "start")
        test_id = resp["session"]
        self.tanks[instance.tank.id]["test_id"] = test_id
        log.info("Test with id=%s started." % test_id)
        self._wait_for_completed(client, instance.tank.id, False)
        instance.status = 'R'
        instance.save()
        client.resume(test_id)
        self._wait_for_completed(client, instance.tank.id, True)
        instance.status = 'F'
        instance.save()
        log.info("Test with id=%s stopped." % test_id)

tank_manager = TankManager()
