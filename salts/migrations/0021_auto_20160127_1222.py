# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salts', '0020_auto_20160127_1217'),
    ]

    operations = [
        migrations.RenameField('TestResult',
                               'generator_type',
                               'generator_type_list')
    ]
