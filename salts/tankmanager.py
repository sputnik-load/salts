# -*- coding: utf-8 -*-

import threading
import time
import os
import json
from salts.logger import Logger
from salts.api_client import TankClient
from salts_prj.settings import LT_PATH


log = Logger.get_logger()


def stg_completed_to_bool(value):
    if type(value) is bool:
        return value

    return value.lower() == "true"


class TankManagerException(Exception):
    pass


class TankManager(object):

    CTRL_C_INTERVAL = 180  # seconds (TESTING-2586)
    POLL_INTERVAL = 5  # seconds
    WAIT_FOR_RESULT_SAVED = 60  # seconds

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
        def format_resp(resp):
            failures = resp.get('failures')
            if failures:
                for fail in failures:
                    fail['reason'] = fail['reason'].split('\n')
            return json.dumps(resp, indent=4)

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
                    log.info("Test %s. Response: %s" % (status, format_resp(resp)))
                    break
                log.info("Test %s. Response: %s" % (status, format_resp(resp)))
            else:
                log.info("Response: %s" % format_resp(resp))
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
        instance.test_id = test_id
        instance.save()
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

    def _change_test_status(self, shooting):
        from salts.models import TestResult
        from datetime import timedelta

        start_time = time.time()
        ctrl_c_delta = timedelta(seconds=TankManager.CTRL_C_INTERVAL)
        while time.time() - start_time <= TankManager.WAIT_FOR_RESULT_SAVED:
            try:
                test_result = TestResult.objects.get(test_id=shooting.test_id)
            except TestResult.DoesNotExist:
                log.info("The test id=%s isn't "
                         "been saved yet." % shooting.test_id)
                time.sleep(TankManager.POLL_INTERVAL)
                continue
            if test_result.dt_finish - test_result.dt_start >= ctrl_c_delta:
                log.info("The test id=%s: "
                         "test duration exceeds 3 minutes, "
                         "the status remains Unknown." % shooting.test_id)
                return
            test_result.test_status = 'dbg'
            test_result.save()
            log.info("The test id=%s: "
                     "test duration less than 3 minutes, "
                     "the status is changed with Debug." % shooting.test_id)
            return
        log.warning("The test id=%s isn't saved into DB." % shooting.test_id)

    def interrupt(self, shooting):
        try:
            client = TankClient(shooting.tank.host, shooting.tank.port)
            resp = client.status(shooting.test_id)
            client.stop(shooting.test_id)
            log.info("The test id=%s is stopped." % shooting.test_id)
            if resp.get('current_stage') == 'poll':
                self._change_test_status(shooting)
            else:
                log.info("Test id=%s won't be saved into DB "
                         "as it hasn't started yet." % shooting.test_id)
        except Exception, exc:
            log.warning("Exception when test "
                        "has been interrupted: %s" % exc)

tank_manager = TankManager()
