# -*- coding: utf-8 -*-

import threading
import time
import os
import shutil
import json
import re
import pickle
import codecs
import ConfigParser
import StringIO
from salts.logger import Logger
from salts_prj.settings import LT_PATH
from tank_api_client import TankClient


log = Logger.get_logger()


class UnicodeConfigParser(ConfigParser.RawConfigParser):
    def __init__(self, *args, **kwargs):
        ConfigParser.RawConfigParser.__init__(self, *args, **kwargs)

    def write(self, fp):
        """Fixed for Unicode output"""
        if self._defaults:
            fp.write("[%s]\n" % "DEFAULT")
            for (key, value) in self._defaults.items():
                fp.write("%s = %s\n" % (key, unicode(value).replace('\n', '\n\t')))
            fp.write("\n")

        for section in self._sections:
            fp.write("[%s]\n" % section)
            for (key, value) in self._sections[section].items():
                if key != "__name__":
                    fp.write("%s = %s\n" % (key, unicode(value).replace('\n','\n\t')))
            fp.write("\n")

    # This function is needed to override default lower-case conversion
    # of the parameter's names. They will be saved 'as is'.
    def optionxform(self, strOut):
        return strOut


def stg_completed_to_bool(value):
    if type(value) is bool:
        return value

    return value.lower() == 'true'


class TankManagerException(Exception):
    pass


class TankManager(object):

    CTRL_C_INTERVAL = 180  # seconds (TESTING-2586)
    POLL_INTERVAL = 5  # seconds
    WAIT_FOR_RESULT_SAVED = 60  # seconds

    def __init__(self):
        self.lock_dir_path = os.path.join(LT_PATH, 'lock')
        if os.path.exists(self.lock_dir_path):
            shutil.rmtree(self.lock_dir_path)
        os.mkdir(self.lock_dir_path)

    def book(self, tank_id):
        lock_path = os.path.join(self.lock_dir_path, '%s.lock' % tank_id)
        if os.path.exists(lock_path):
            return False
        open(lock_path, 'w').close()
        return True

    def free(self, tank_id):
        lock_path = os.path.join(self.lock_dir_path, '%s.lock' % tank_id)
        if not os.path.exists(lock_path):
            return False
        os.unlink(lock_path)
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
                    log.info("Test %s. Response: %s" \
                             % (status, format_resp(resp)))
                    break
                log.info("Test %s. Response: %s" \
                         % (status, format_resp(resp)))
            else:
                log.info("Response: %s" % format_resp(resp))

    def shoot(self, **kwargs):
        custom_data = kwargs.get('custom_data')
        scenario = kwargs.get('scenario')
        tank = kwargs.get('tank')
        client = TankClient(tank.host, tank.port)
        config_path = os.path.join(LT_PATH, scenario.scenario_path)
        config = UnicodeConfigParser()
        config.readfp(codecs.open(config_path, 'r', 'utf-8'))
        custom = json.loads(custom_data)
        for sec in custom:
            if not config.has_section(sec):
                config.add_section(sec)
            param = custom[sec]
            for k in param:
                config.set(sec, k, param[k])
        final_config = StringIO.StringIO()
        config.write(final_config)
        content = final_config.getvalue().encode('utf-8')
        resp = None
        resp = client.run(content, 'start')
        session_id = resp['session']
        log.info("Test with id=%s started." % session_id)
        self._wait_for_completed(client, session_id, tank.id, False)
        client.resume(session_id)
        self._wait_for_completed(client, session_id, tank.id, True)
        log.info("Test with id=%s stopped." % session_id)

    def _change_test_status(self, **kwargs):
        from salts.models import TestResult
        from datetime import timedelta

        shooting = kwargs.get('shooting')
        start_time = time.time()
        ctrl_c_delta = timedelta(seconds=TankManager.CTRL_C_INTERVAL)
        while time.time() - start_time <= TankManager.WAIT_FOR_RESULT_SAVED:
            try:
                test_result = \
                    TestResult.objects.get(session_id=shooting.session_id)
            except TestResult.DoesNotExist:
                log.info("The test id=%s isn't "
                         "been saved yet." % shooting.session_id)
                time.sleep(TankManager.POLL_INTERVAL)
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
                     "the status is changed with Debug." \
                     % shooting.session_id)
            return
        log.warning("The test id=%s isn't saved into DB." \
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
        log.info("TankManager.interrupt. Shooting.session_id: %s" \
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
