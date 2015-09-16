# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('salts', '0005_auto_20150608_1553'),
    ]

    operations = [
        migrations.AddField(
            model_name='testresult',
            name='console_log',
            field=models.FileField(upload_to=b'results/%Y/%m/%d', null=True, verbose_name=b'\xd0\x9b\xd0\xbe\xd0\xb3 \xd0\xba\xd0\xbe\xd0\xbd\xd1\x81\xd0\xbe\xd0\xbb\xd0\xb8', blank=True),
            preserve_default=True,
        ),
    ]
