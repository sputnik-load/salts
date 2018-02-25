# -*- coding: utf-8 -*-

import slumber


from requests.auth import AuthBase

class TastypieApikeyAuth(AuthBase):
    def __init__(self, username, apikey):
        self.username = username
        self.apikey = apikey

    def __call__(self, r):
        r.headers['Authorization'] = "ApiKey {0}:{1}".format(self.username, self.apikey)
        return r


class DRFApikeyAuth(AuthBase):
    def __init__(self, apikey):
        self.apikey = apikey

    def __call__(self, r):
        r.headers['Authorization'] = "Token {0}".format(self.apikey)
        return r


try:
    #api_url = "http://<SALTS_TEST_HOSTNAME>:8000/api2/"
    api_url = "http://<SALTS_HOSTNAME>/api2/"
    try:
        api = slumber.API(api_url, auth=DRFApikeyAuth("6574ce5cf1a5260a1c20394e182976439e977a9c"))
    except Exception, exc:
        print "exception: %s" % exc
        exit(1)
    print "api: %s" % api
    old = api.get()
    print "old: %s" % old
    old = api.testresult.get(session_id="2016-03-11_09-00-00.G2TESB")
    print "old: %s" % old
    gen_types = ["jmeter", "phantom"]
    gen_type_objects = [api.generatortype.get(name=gt)[0]
                        for gt in gen_types]
    if old:
        print "OLD: %s" % old
        api.testresult(old[0]['id']).delete()
    new = api.testresult.post({"session_id": "2016-03-11_09-00-00.G2TESB",
                               "dt_start": "2016-03-11T08:00:00",
                               "dt_finish": "2016-03-11T09:00:00",
                               "group": "Тест",
                               "test_name": "Тест CONST",
                               "target": "127.0.0.1:80",
                               "version": "0.0.1",
                               "rps": "5", "q99": "99", "q90": "90",
                               "q50": "50", "http_errors_perc": "0.01",
                               "net_errors_perc": "0.02",
                               "graph_url": "http://<GRAFANA_URL>/#/dashboard/db/tankresultstpl?var-system=<SYSTEM>&from=20150204T122254&to=20150204T125434", "generator": "localhost", "user": "@user", "ticket_id": "TESTING-001", "mnt_url": "https://<WIKI_URL>/pages/viewpage.action?pageId=12353589",
                               "generator_types": gen_type_objects,
                               "comments": ""})
    print "ID: %s." % new["id"]
    tr = api.testresult(new["id"])
    print "new[generator_types]: %s" % new["generator_types"]
    with open('test1.txt') as fp:
        tr.put(files={'metrics': fp})
    with open('test2.txt') as fp:
        api.testresult(new['id']).put(files={'yt_log': fp})
    api.testresult(new["id"]).put({"test_status": "dbg",
                                   "dt_finish": "2016-03-11T09:11:11Z",
                                   "generator_types": gen_type_objects})
    new = api.testresult.get(session_id="2016-03-11_09-00-00.G2TESB")
    print "new.metrics: %s" % new[0]["metrics"]
    print "new.yt_log: %s" % new[0]["yt_log"]
    print "new.test_status: %s" % new[0]["test_status"]
    print "new.dt_finish: %s" % new[0]["dt_finish"]
    sh = api.shooting.get(id=25)[0]
    api.shooting(25).put({'status': 'R', 'tank': sh['tank'], 'test_ini': sh['test_ini']})
    sh = api.shooting.get(id=25)
    print "sh.status: %s" % sh[0]['status']
except Exception as exc:
    print "Error sending results to salts: " + str(exc)
    if hasattr(exc, 'content'):
        print "Exception content: " + str(exc.content)
    print "Exception : " + repr(exc)
