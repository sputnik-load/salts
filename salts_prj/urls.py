# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.http import HttpResponseRedirect
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from salts_prj.views import tests_list, run_test_api, stop_test_api, status_test_api
admin.autodiscover()

import settings

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'salts.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^favicon.ico/$', lambda x: HttpResponseRedirect(settings.STATIC_URL+'favicon.ico')), #google chrome favicon fix
    url(r'^tests/$', tests_list),
    url(r'^run_test/$', run_test_api),
    url(r'^stop_test/$', stop_test_api),
    url(r'^status_test/$', status_test_api)
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$',
            'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT, }),
    )
    urlpatterns += staticfiles_urlpatterns()


from tastypie.api import Api
from salts.api import TestResultResource

v1_api = Api(api_name='v1')
v1_api.register(TestResultResource())

urlpatterns += patterns('',
    (r'^api/', include(v1_api.urls)),
)


from rest_framework import routers
from salts.api2 import TestResultViewSet
# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'testresult', TestResultViewSet)


urlpatterns += patterns('',
    url(r'^api2-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api2/', include(router.urls)),
)
