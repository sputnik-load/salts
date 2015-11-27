# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salts', '0012_auto_20151127_0925'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testsettings',
            name='test_name',
            field=models.CharField(help_text=b'\xd0\x9d\xd0\xb0\xd0\xb7\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5 \xd1\x82\xd0\xb5\xd1\x81\xd1\x82\xd0\xb0', max_length=512, null=True, verbose_name=b'\xd0\xa2\xd0\xb5\xd1\x81\xd1\x82', blank=True),
        ),
    ]
