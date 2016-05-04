import requests
import simplejson as json
from time import sleep
from logger import Logger


log = Logger.get_logger()


class TankClientError(Exception):
    pass


class TankClient(object):

    REQ_INTERVAL = 3

    def __init__(self, api_address, api_port):
        self.api_address = api_address
        self.api_port = api_port
        self.log = log
        self._test_connection()

    def _test_connection(self):
        req = "http://{api_address}:{api_port}/status".format(
                api_address=self.api_address,
                api_port=self.api_port)
        while True:
            try:
                requests.get(req)
                break
            except requests.ConnectionError, exc:
                self.log.info("Yandex Tank Api Server on {api_address}:{api_port} isn't available.".format(
                                api_address=self.api_address,
                                api_port=self.api_port))
                sleep(TankClient.REQ_INTERVAL)

    def run(self, config, breakpoint="finished", test_id=None):
        req = "http://{api_address}:{api_port}/run?break={breakpoint}".format(
            api_address=self.api_address,
            api_port=self.api_port,
            breakpoint=breakpoint,
        )
        if test_id:
            req += "&test=%s" % test_id
        resp = requests.post(req, data=config)
        if resp.status_code == 200:
            data = json.loads(resp.text)
            return data
        else:
            raise TankClientError("Test Run Error: %s" % resp.text)

    def resume(self, session_id, breakpoint="finished"):
        req = "http://{api_address}:{api_port}/run?break={breakpoint}&session={session}".format(
            api_address=self.api_address,
            api_port=self.api_port,
            breakpoint=breakpoint,
            session=session_id,
        )
        resp = requests.get(req)
        if resp.status_code == 200:
            data = json.loads(resp.text)
            return data
        else:
            raise TankClientError("Test Resume Error: %s" % resp.text)

    def stop(self, session_id):
        req = "http://{api_address}:{api_port}/stop?session={session}".format(
            api_address=self.api_address,
            api_port=self.api_port,
            session=session_id
        )
        resp = requests.get(req)
        if resp.status_code == 200:
            data = json.loads(resp.text)
            return data
        else:
            raise TankClientError("Test Stop Error: %s" % resp.text)

    def test_id(self, session_id):
        req = "http://{api_address}:{api_port}/artifact?session={session}".format(
            api_address=self.api_address,
            api_port=self.api_port,
            session=session_id
        )
        resp = requests.get(req)
        if resp.status_code == 200:
            data = json.loads(resp.text)
            return data
        else:
            raise TankClientError("Test ID Error: %s" % resp.text)

    def list_artifacts(self, test_id):
        req = "http://{api_address}:{api_port}/artifact?test={test}".format(
            api_address=self.api_address,
            api_port=self.api_port,
            test=test_id
        )
        resp = requests.get(req)
        if resp.status_code == 200:
            data = json.loads(resp.text)
            return data
        else:
            raise TankClientError("Test List Artifact Error: %s" % resp.text)

    def get_artifact(self, test_id, filename):
        req = "http://{api_address}:{api_port}/artifact?test={test}&filename={filename}".format(
            api_address=self.api_address,
            api_port=self.api_port,
            test=test_id,
            filename=filename,
        )
        resp = requests.get(req)
        if resp.status_code == 200:
            data = resp.text
            return data
        else:
            raise TankClientError("Test Get Artifact Error: %s" % resp.text)

    def status(self, session_id=None):
        req = "http://{api_address}:{api_port}/status".format(
            api_address=self.api_address,
            api_port=self.api_port,
        )
        if session_id:
            req += "?session=%s" % session_id
        resp = requests.get(req)
        if resp.status_code == 200:
            data = json.loads(resp.text)
            return data
        else:
            raise TankClientError("Test Status Error: %s" % resp.text)
