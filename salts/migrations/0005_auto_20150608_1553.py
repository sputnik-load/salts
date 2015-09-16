# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('salts', '0004_testresult_metrics'),
    ]

    operations = [
        migrations.AddField(
            model_name='testresult',
            name='jm_log',
            field=models.FileField(upload_to=b'results/%Y/%m/%d', null=True, verbose_name=b'\xd0\x9b\xd0\xbe\xd0\xb3 jmeter', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='testresult',
            name='modified_jmx',
            field=models.FileField(upload_to=b'results/%Y/%m/%d', null=True, verbose_name=b'modified.jmx', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='testresult',
            name='ph_conf',
            field=models.FileField(upload_to=b'results/%Y/%m/%d', null=True, verbose_name=b'\xd0\x9a\xd0\xbe\xd0\xbd\xd1\x84\xd0\xb8\xd0\xb3 phantom', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='testresult',
            name='yt_conf',
            field=models.FileField(upload_to=b'results/%Y/%m/%d', null=True, verbose_name=b'\xd0\x9a\xd0\xbe\xd0\xbd\xd1\x84\xd0\xb8\xd0\xb3 yandex-tank', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='testresult',
            name='yt_log',
            field=models.FileField(upload_to=b'results/%Y/%m/%d', null=True, verbose_name=b'\xd0\x9b\xd0\xbe\xd0\xb3 yandex-tank', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='testresult',
            name='metrics',
            field=models.FileField(upload_to=b'results/%Y/%m/%d', null=True, verbose_name=b'\xd0\x9c\xd0\xb5\xd1\x82\xd1\x80\xd0\xb8\xd0\xba\xd0\xb8', blank=True),
            preserve_default=True,
        ),
    ]
