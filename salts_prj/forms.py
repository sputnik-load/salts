# -*- coding: utf-8 -*-

from django import forms
from salts.models import TestResult


class TestResultEditForm(forms.ModelForm):
    class Meta:
        model = TestResult
        fields = ['test_name', 'test_status', 'comments']

    test_name = forms.CharField(
        widget=forms.TextInput(attrs={'readonly':'readonly'}))
    test_status = forms.ChoiceField(label='', initial='',
                                    choices=TestResult.TEST_STATUS_CHOICES,
                                    widget=forms.Select())
    comments = forms.Textarea()
