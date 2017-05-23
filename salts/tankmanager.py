# -*- coding: utf-8 -*-

import threading
import time
import os
import json
import re
import pickle
from salts_prj.settings import LT_PATH
from salts_prj.settings import log
from tank_api_client import TankClient, TankClientError
from tank_api_client.confighelper import CustomConfig


def remainedtime(shooting):
    remained = 0
    if shooting.planned_duration:
        if shooting.planned_duration == -1:
            return -1
        if shooting.start:
            if shooting.status == 'I':
                ts = shooting.finish
                if not ts:
                    ts = shooting.start
            else:
                ts = int(time.time() + 0.5)
            if shooting.status == 'P':
                remained = shooting.planned_duration
            else:
                remained = shooting.planned_duration - (ts - shooting.start)
        else:
            remained = shooting.planned_duration
    if remained < 0:
        remained = 0

    return remained


def stg_completed_to_bool(value):
    if type(value) is bool:
        return value

    return value.lower() == 'true'


class TankManagerException(Exception):
    pass


class TankManager(object):

    CTRL_C_INTERVAL = 180  # seconds (TESTING-2586)
    POLL_INTERVAL = 5  # seconds
    WAIT_INTERVAL = 1  # seconds
    WAIT_FOR_RESULT_SAVED = 60  # seconds

    def __init__(self):
        self.lock_dir_path = "/tmp/lock"
        i = 0
        base = self.lock_dir_path
        while os.path.exists(self.lock_dir_path):
            i += 1
            self.lock_dir_path = "{path}-{index}".format(path=base, index=i)
        os.mkdir(self.lock_dir_path)

    def book(self, tank_id):
        lock_path = os.path.join(self.lock_dir_path, '%s.lock' % tank_id)
        if os.path.exists(lock_path):
            return False
        open(lock_path, 'w').close()
        log.info("Tank with id=%s was busy." % tank_id)
        return True

    def free(self, tank_id):
        lock_path = os.path.join(self.lock_dir_path, '%s.lock' % tank_id)
        if not os.path.exists(lock_path):
            return False
        os.unlink(lock_path)
        log.info("Tank with id=%s became free." % tank_id)
        return True

    def _check_for_running(self, client):
        while True:
            resp = client.status()
            running = False
            for sess_id in resp:
                if resp[sess_id]["status"] == "running":
                    log.info("Test can't start because other "
                             "test with id=%s is running now." % sess_id)
                    running = True
                    break
            if not running:
                break
            time.sleep(TankManager.POLL_INTERVAL)

    def _wait_for_completed(self, client, session_id,
                            tank_id, expected_retcode):
        def format_resp(resp):
            failures = resp.get('failures')
            if failures:
                for fail in failures:
                    fail['reason'] = fail['reason'].split('\n')
            return json.dumps(resp, indent=4)

        while True:
            resp = client.status(session_id)
            if "stage_completed" in resp:
                status = resp["status"]
                completed = stg_completed_to_bool(resp["stage_completed"])
                if expected_retcode:
                    if resp["retcode"] is None:
                        completed = False
                if completed:
                    log.debug("Test %s. Response: %s"
                              % (status, format_resp(resp)))
                    return resp
                log.debug("Test %s. Response: %s"
                          % (status, format_resp(resp)))
            else:
                log.debug("Response: %s" % format_resp(resp))
            time.sleep(TankManager.WAIT_INTERVAL)

    def _wait_for_status(self, client, session_id):
        while True:
            resp = client.status(session_id)
            if "status" not in resp:
                log.warning("Response doesn't contain the 'status' field. "
                            "Test with id=%s. Response: %s"
                            % (session_id, resp))
                return resp
            if resp["status"] == "running":
                time.sleep(TankManager.WAIT_INTERVAL)
                continue
            return resp

    def shoot(self, **kwargs):
        custom_data = kwargs.get('custom_data')
        scenario = kwargs.get('scenario')
        tank = kwargs.get('tank')
        client = TankClient(tank.host, tank.port)
        config = CustomConfig(os.path.join(LT_PATH, scenario.scenario_path))
        config.mergejson(custom_data)
        resp = None
        resp = client.run(config.textcontent(), 'start')
        session_id = resp['session']
        log.info("Test with id=%s started." % session_id)
        self._wait_for_completed(client, session_id, tank.id, False)
        client.resume(session_id)
        response = self._wait_for_completed(client, session_id, tank.id, True)
        log.info("Test with id=%s stopped." % session_id)
        return response

    def shootmq(self, tank, scenario, custom_data):
        tank_fields = tank[0]["fields"]
        tank_id = tank[0]["pk"]
        scenario_fields = scenario[0]["fields"]
        try:
            client = TankClient(tank_fields["host"], tank_fields["port"])
        except TankClientError, exc:
            resp = {"status": "failed",
                    "failures": [
                        {
                            "reason": str(exc),
                            "stage": "prepare"
                        }
                    ]}
            return resp

        config = CustomConfig(os.path.join(LT_PATH,
                                           scenario_fields["scenario_path"]))
        config.mergejson(custom_data)
        resp = None
        resp = client.run(config.textcontent(), "start")
        session_id = resp["session"]
        log.info("Test with id=%s started." % session_id)
        self._wait_for_completed(client, session_id, tank_id, False)
        client.resume(session_id)
        self._wait_for_completed(client, session_id, tank_id, True)
        resp = self._wait_for_status(client, session_id)
        log.info("Test with id=%s stopped." % session_id)
        return resp

    def _change_test_status(self, **kwargs):
        from salts.models import TestResult
        from datetime import timedelta

        shooting = kwargs.get('shooting')
        start_time = time.time()
        ctrl_c_delta = timedelta(seconds=TankManager.CTRL_C_INTERVAL)
        curr_time = time.time()
        while curr_time - start_time <= TankManager.WAIT_FOR_RESULT_SAVED:
            try:
                test_result = \
                    TestResult.objects.get(session_id=shooting.session_id)
            except TestResult.DoesNotExist:
                log.info("The test id=%s isn't "
                         "been saved yet." % shooting.session_id)
                time.sleep(TankManager.POLL_INTERVAL)
                curr_time = time.time()
                continue
            if test_result.dt_finish - test_result.dt_start >= ctrl_c_delta:
                log.info("The test id=%s: "
                         "test duration exceeds 3 minutes, "
                         "the status remains Unknown." % shooting.session_id)
                return
            test_result.test_status = 'dbg'
            test_result.save()
            log.info("The test id=%s: "
                     "test duration less than 3 minutes, "
                     "the status is changed with Debug."
                     % shooting.session_id)
            return
        log.warning("The test id=%s wasn't saved into DB."
                    % shooting.session_id)

    def interrupt(self, shooting):
        resp = None
        if re.match('\d+_0+', shooting.session_id):
            try:
                client = TankClient(shooting.tank.host, shooting.tank.port)
                resp = client.status(shooting.session_id)
                client.stop(shooting.session_id)
            except Exception, exc:
                log.info("Exception when test "
                         "has been interrupted: %s" % exc)
        log.info("TankManager.interrupt. Shooting.session_id: %s"
                 % shooting.session_id)
        try:
            log.info("The test id=%s is stopped." % shooting.session_id)
            self.free(shooting.tank.id)
            if (resp and resp.get('current_stage') == 'poll') \
               or (not resp and shooting.status != 'P'):
                thread_data = {'shooting': shooting}
                t = threading.Thread(name="Change Test Status",
                                     target=self._change_test_status,
                                     kwargs=thread_data)
                t.start()
            else:
                log.info("Test id=%s won't be saved into DB "
                         "as it hasn't started yet." % shooting.session_id)
        except Exception, exc:
            log.warning("Exception when test "
                        "has been interrupted: %s" % exc)

    def save_to_lock(self, tank_id, key, value):
        if value is None:
            return
        lock_path = os.path.join(self.lock_dir_path, '%s.lock' % tank_id)
        if os.path.exists(lock_path):
            data = {}
            with open(lock_path, 'rb') as f:
                try:
                    data = pickle.load(f)
                except EOFError:
                    data = {}
            data[key] = value
            with open(lock_path, 'wb') as f:
                pickle.dump(data, f)

    def read_from_lock(self, tank_id, key):
        lock_path = os.path.join(self.lock_dir_path, '%s.lock' % tank_id)
        if os.path.exists(lock_path):
            with open(lock_path, 'rb') as f:
                try:
                    data = pickle.load(f)
                except EOFError:
                    data = {}
                return data.get(key)
        return None


tank_manager = TankManager()
