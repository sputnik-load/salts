# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('salts', '0003_auto_20150413_1709'),
    ]

    operations = [
        migrations.AddField(
            model_name='testresult',
            name='metrics',
            field=models.FileField(upload_to=b'results/%Y/%m/%d', null=True, verbose_name=b'\xd0\xa0\xd0\xb5\xd0\xb7\xd1\x83\xd0\xbb\xd1\x8c\xd1\x82\xd0\xb0\xd1\x82\xd1\x8b \xd0\x9d\xd0\xa2 - \xd0\xbc\xd0\xb5\xd1\x82\xd1\x80\xd0\xb8\xd0\xba\xd0\xb8', blank=True),
            preserve_default=True,
        ),
    ]
