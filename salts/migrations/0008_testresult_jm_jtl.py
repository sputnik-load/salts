# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('salts', '0007_testresult_report_txt'),
    ]

    operations = [
        migrations.AddField(
            model_name='testresult',
            name='jm_jtl',
            field=models.FileField(upload_to=b'results/%Y/%m/%d', null=True, verbose_name=b'jtl-\xd0\xbb\xd0\xbe\xd0\xb3 jmeter (\xd1\x81\xd1\x8b\xd1\x80\xd1\x8b\xd0\xb5 \xd1\x80\xd0\xb5\xd0\xb7\xd1\x83\xd0\xbb\xd1\x8c\xd1\x82\xd0\xb0\xd1\x82\xd1\x8b)', blank=True),
            preserve_default=True,
        ),
    ]
