# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('salts', '0009_auto_20150608_1841'),
    ]

    operations = [
        migrations.AddField(
            model_name='testresult',
            name='jm_log_2',
            field=models.FileField(upload_to=b'results/%Y/%m/%d', null=True, verbose_name=b'\xd0\x94\xd0\xbe\xd0\xbf\xd0\xbe\xd0\xbb\xd0\xbd\xd0\xb8\xd1\x82\xd0\xb5\xd0\xbb\xd1\x8c\xd0\xbd\xd1\x8b\xd0\xb9 \xd0\xbb\xd0\xbe\xd0\xb3 jmeter (testResults.txt)', blank=True),
            preserve_default=True,
        ),
    ]
