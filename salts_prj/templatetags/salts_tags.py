# -*- coding: utf-8 -*-
import os
import datetime
from django import template
from django.conf import settings
from django.core.urlresolvers import reverse

register = template.Library()


@register.simple_tag
def active(request, url):
    if request.path.startswith(reverse(url)):
        return 'active'
    return ''

@register.simple_tag
def duration(dt_start, dt_finish):
    return dt_finish - dt_start
