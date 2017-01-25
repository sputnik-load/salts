# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.http import HttpResponseRedirect
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.contrib.auth import views
from django.views.generic import RedirectView
from salts_prj.views import run_test_api, stop_test_api, status_test_api
from salts_prj.views import show_test_settings, edit_test_parameters, poll_servers
from salts_prj.views import show_results_page, get_results
from salts_prj.views import show_trends_page, tank_monitoring, get_tank_status
from salts_prj.views import salts_logout, get_version
from salts_prj.views import gitsync, edit_testresult, update_testresult
from salts_prj.shooter import ShooterView
from salts_prj.scenariorun import ScenarioRunView

admin.autodiscover()

import settings

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'salts.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', RedirectView.as_view(url='/results/')),
    url(r'^login/', views.login, name="login"),
    url(r'^logout/', salts_logout, name="logout"),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^favicon.ico/$', lambda x: HttpResponseRedirect(settings.STATIC_URL+'favicon.ico')), #google chrome favicon fix
    url(r'^tests/$', show_test_settings),
    url(r'^tests/(\d+)/$', edit_test_parameters),
    url(r'^run_test/$', run_test_api),
    url(r'^stop_test/$', stop_test_api),
    url(r'^status_test/$', status_test_api),
    url(r'^poll_servers/$', poll_servers),
    url(r'^tanks/$', tank_monitoring, name='tank_monitoring'),
    url(r'^get_tank_status/$', get_tank_status),
    url(r'^results/$', show_results_page, name='test_results'),
    url(r'^get_results/$', get_results),
    url(r'^results/graph/$', show_trends_page),
    url(r'^gitsync/$', gitsync),
    url(r'^edit/$', edit_testresult),
    url(r'^version/$', get_version),
    url(r'^update/$', update_testresult),
    url(r'^shoot/$', ShooterView.as_view()),
    url(r'^run/$', ScenarioRunView.as_view(), name='run_test'),
    url(r'^qunit/', include('django_qunit.urls')),
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
from salts.api2 import (TestResultViewSet, GeneratorTypeViewSet,
                        GeneratorTypeListViewSet, ShootingViewSet,
                        ScenarioViewSet, TankViewSet, GroupViewSet,
                        UserViewSet)

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'testresult', TestResultViewSet)
router.register(r'generatortype', GeneratorTypeViewSet)
router.register(r'generatortypelist', GeneratorTypeListViewSet)
router.register(r'shooting', ShootingViewSet)
router.register(r'group', GroupViewSet)
router.register(r'scenario', ScenarioViewSet)
router.register(r'tank', TankViewSet)
router.register(r'user', UserViewSet)


urlpatterns += patterns('',
    url(r'^api2-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api2/', include(router.urls)),
)
