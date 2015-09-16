# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('salts', '0006_testresult_console_log'),
    ]

    operations = [
        migrations.AddField(
            model_name='testresult',
            name='report_txt',
            field=models.FileField(upload_to=b'results/%Y/%m/%d', null=True, verbose_name=b'\xd0\xa2\xd0\xb5\xd0\xba\xd1\x81\xd1\x82\xd0\xbe\xd0\xb2\xd1\x8b\xd0\xb9 \xd0\xbe\xd1\x82\xd1\x87\xd0\xb5\xd1\x82 SputnikReport', blank=True),
            preserve_default=True,
        ),
    ]
