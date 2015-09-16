# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('salts', '0002_auto_20150318_1221'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testresult',
            name='group',
            field=models.CharField(help_text=b'\xd0\x9f\xd1\x80\xd0\xbe\xd0\xb4\xd1\x83\xd0\xba\xd1\x82 \xd0\xba \xd0\xba\xd0\xbe\xd1\x82\xd0\xbe\xd1\x80\xd0\xbe\xd0\xbc\xd1\x83 \xd0\xbe\xd1\x82\xd0\xbd\xd0\xbe\xd1\x81\xd0\xb8\xd1\x82\xd1\x81\xd1\x8f \xd1\x82\xd0\xb5\xd1\x81\xd1\x82', max_length=32, null=True, verbose_name=b'\xd0\x9f\xd1\x80\xd0\xbe\xd0\xb4\xd1\x83\xd0\xba\xd1\x82', blank=True),
            preserve_default=True,
        ),
    ]
