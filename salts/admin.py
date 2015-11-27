# -*- coding: utf-8 -*-
from django.contrib import admin
from salts.models import *

# Register your models here.
class TestResultAdmin(admin.ModelAdmin):
    #list_display = ('id', 'status', 'test_status', 'dt_start', 'dt_finish', 'results')
    list_display = ('test_name', 'group', 'version', 'test_status', 'rps', 'show_test_len', 'q99', 'q90', 'q50', 'http_errors_perc', 'net_errors_perc', 'generator', 'target', 'show_graph_url', 'user', 'ticket_id', 'test_id', )
    list_filter = ['group', 'test_status', 'generator', 'user', 'target']
    readonly_fields = ('meta',)

    def show_graph_url(self, instance):
        return str('<a href="%s">graphs</a>' % (instance.graph_url.decode()))
    show_graph_url.allow_tags = True
    def show_test_len(self, instance):
        return str('%s' % (instance.dt_finish - instance.dt_start))

admin.site.register(TestResult, TestResultAdmin)
