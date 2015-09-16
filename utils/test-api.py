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


api_url = "http://salt-dev.dev.ix.km/api/v1/"
#api = slumber.API(api_url, auth=TastypieApikeyAuth("ltbot", "5793922b4b5cc7ff42a6b348c1011f133abb25fc"))
#new = api.testresult.post({"test_id": "2016-03-11_09-00-00.G2TESB", "dt_start": "2016-03-11T08:00:00", "dt_finish": "2016-03-11T09:00:00", "group": "Тест", "test_name": "Тест CONST", "target": "127.0.0.1:80", "version": "0.0.1", "rps": "5", "q99": "99", "q90": "90", "q50": "50", "http_errors_perc": "0.01", "net_errors_perc": "0.02", "graph_url": "http://grafana-test.ix.km/#/dashboard/db/tankresultstpl?var-system=search&var-collector=index-113&from=20150204T122254&to=20150204T125434", "generator": "localhost", "user": "@user", "ticket_id": "TESTING-001", "mnt_url": "https://wiki.amalama.ru/pages/viewpage.action?pageId=12353589", "comments": ""})
#print "new=" + new


class DRFApikeyAuth(AuthBase):
    def __init__(self, apikey):
        self.apikey = apikey

    def __call__(self, r):
        r.headers['Authorization'] = "Token {0}".format(self.apikey)
        return r


try:
    #api_url = "http://salt-dev.dev.ix.km/api2/"
    api_url = "http://127.0.0.1:8000/api2/"
    api = slumber.API(api_url, auth=DRFApikeyAuth("8111a8d18f8e4cb4923c605238c954db85f8edb7"))
    old = api.testresult.get(test_id="2016-03-11_09-00-00.G2TESB")
    api.testresult(old[0]['id']).delete()
    new = api.testresult.post({"test_id": "2016-03-11_09-00-00.G2TESB", "dt_start": "2016-03-11T08:00:00", "dt_finish": "2016-03-11T09:00:00", "group": "Тест", "test_name": "Тест CONST", "target": "127.0.0.1:80", "version": "0.0.1", "rps": "5", "q99": "99", "q90": "90", "q50": "50", "http_errors_perc": "0.01", "net_errors_perc": "0.02", "graph_url": "http://grafana-test.ix.km/#/dashboard/db/tankresultstpl?var-system=search&var-collector=index-113&from=20150204T122254&to=20150204T125434", "generator": "localhost", "user": "@user", "ticket_id": "TESTING-001", "mnt_url": "https://wiki.amalama.ru/pages/viewpage.action?pageId=12353589", "comments": ""})
    with open('test1.txt') as fp:
        api.testresult(new['id']).put(files={'metrics': fp})
    with open('test2.txt') as fp:
        api.testresult(new['id']).put(files={'yt_log': fp})
    #print "new=" + str(new)
except Exception as exc:
    print "Error sending results to salts: " + str(exc)
    if hasattr(exc, 'content'):
        print "Exception content: " + str(exc.content)
    print "Exception : " + repr(exc)
