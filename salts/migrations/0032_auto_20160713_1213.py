# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salts', '0031_auto_20160713_1011'),
    ]

    operations = [
        migrations.RenameModel('TestIni', 'Scenario'),
        migrations.RenameField('Shooting', 'test_ini', 'scenario')
    ]
