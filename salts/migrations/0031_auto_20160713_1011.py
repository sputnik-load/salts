# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salts', '0030_auto_20160712_1511'),
    ]

    operations = [
        migrations.RenameField('TestResult', 'scenario_id', 'scenario_path'),
        migrations.RenameField('TestIni', 'scenario_id', 'scenario_path')
    ]
