# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salts', '0019_auto_20160127_1204'),
    ]

    operations = [
        migrations.RenameModel('GeneratorType', 'GeneratorTypeList')
    ]
