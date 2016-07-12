import requests
import simplejson as json


class TankClient(object):
    def __init__(self, api_address, api_port, logger):
        self.api_address = api_address
        self.api_port = api_port
        self.logger = logger

    def run(self, config, breakpoint="finished", session_id=None):
        req = "http://{api_address}:{api_port}/run?break={breakpoint}".format(
            api_address=self.api_address,
            api_port=self.api_port,
            breakpoint=breakpoint,
        )
        if session_id:
            req += "&test=%s" % session_id
        resp = requests.post(req, data=config)
        if resp.status_code == 200:
            data = json.loads(resp.text)
            return data
        else:
            self.logger.info("No run: " + resp.text)
            return None

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
            self.logger.info("No resume: " + resp.text)
            return None

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
            self.logger.info("No stop: " + resp.text)
            return None

    def session_id(self, session_id):
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
            self.logger.info("No test id: " + resp.text)
            return None

    def list_artifacts(self, session_id):
        req = "http://{api_address}:{api_port}/artifact?test={test}".format(
            api_address=self.api_address,
            api_port=self.api_port,
            test=session_id
        )
        resp = requests.get(req)
        if resp.status_code == 200:
            data = json.loads(resp.text)
            return data
        else:
            self.logger.info("No list_artifacts: " + resp.text)
            return None

    def get_artifact(self, session_id, filename):
        req = "http://{api_address}:{api_port}/artifact?test={test}&filename={filename}".format(
            api_address=self.api_address,
            api_port=self.api_port,
            test=session_id,
            filename=filename,
        )
        resp = requests.get(req)
        if resp.status_code == 200:
            data = resp.text
            return data
        else:
            self.logger.info("No get artifact: " + resp.text)
            return None

    def status(self, session_id=None):
        req = "http://{api_address}:{api_port}/status".format(
            api_address=self.api_address,
            api_port=self.api_port,
        )
        if session_id:
            req += "?%s" % session_id
        resp = requests.get(req)
        if resp.status_code == 200:
            data = json.loads(resp.text)
            return data
        else:
            self.logger.info("No status: " + resp.text)
            return None
