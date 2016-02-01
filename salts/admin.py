# -*- coding: utf-8 -*-
from django.contrib import admin
from django import forms
from salts.models import *


class TestResultAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TestResultAdminForm, self).__init__(*args, **kwargs)
        self.fields['comments'].widget = admin.widgets.AdminTextareaWidget()


# Register your models here.
class TestResultAdmin(admin.ModelAdmin):
    form = TestResultAdminForm
    #list_display = ('id', 'status', 'test_status', 'dt_start', 'dt_finish', 'results')
    list_display = ('id', 'test_name', 'group', 'version', 'test_status', 'comments',
                    'rps', 'show_test_len', 'q99', 'q90', 'q50',
                    'http_errors_perc', 'net_errors_perc', 'generator', 'target',
                    'show_graph_url', 'user', 'ticket_id', 'test_id', 'scenario_id',)
    list_display_links = ('id', 'test_id', )
    list_filter = ('group', 'test_status', 'generator', 'user', )
    list_editable = ('test_name', 'test_status', 'comments', 'rps', 'ticket_id',
                     'scenario_id',)
    list_per_page = 15
    readonly_fields = ('meta',)
    search_fields = ('test_name', 'group', 'target', 'scenario_id', 'ticket_id', 'test_id', )

    def show_graph_url(self, instance):
        return u'<a href="%s">Графики</a>' % (instance.graph_url.decode())
    show_graph_url.allow_tags = True
    def show_test_len(self, instance):
        return str('%s' % (instance.dt_finish - instance.dt_start))



admin.site.register(TestResult, TestResultAdmin)
admin.site.register(GeneratorType, admin.ModelAdmin)
admin.site.register(GeneratorTypeList, admin.ModelAdmin)
admin.site.register(Generator, admin.ModelAdmin)
admin.site.register(Target, admin.ModelAdmin)
admin.site.register(TestSettings, admin.ModelAdmin)
admin.site.register(RPS, admin.ModelAdmin)
admin.site.register(TestRun, admin.ModelAdmin)
