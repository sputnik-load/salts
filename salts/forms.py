# -*- coding: utf-8 -*-

from django import forms
from salts.models import TestSettings, RPS


class SettingsEditForm(forms.ModelForm):
    class Meta:
        model = TestSettings
        fields = ["test_name", "generator",
                  "ticket", "version"]


class RPSEditForm(forms.ModelForm):
    class Meta:
        model = RPS
        fields = ["target", "rps_name", "schedule"]
