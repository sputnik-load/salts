# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('salts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testresult',
            name='test_id',
            field=models.CharField(null=True, max_length=32, blank=True, help_text=b'ID \xd1\x82\xd0\xb5\xd1\x81\xd1\x82\xd0\xb0', unique=True, verbose_name=b'ID'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='testresult',
            name='test_status',
            field=models.CharField(default=b'unk', help_text=b'\xd0\xa4\xd0\xb8\xd0\xbd\xd0\xb0\xd0\xbb\xd1\x8c\xd0\xbd\xd1\x8b\xd0\xb9 \xd1\x81\xd1\x82\xd0\xb0\xd1\x82\xd1\x83\xd1\x81 \xd1\x82\xd0\xb5\xd1\x81\xd1\x82\xd0\xb0 - Pass \xd0\xb8\xd0\xbb\xd0\xb8 Fail.', max_length=4, verbose_name=b'\xd0\xa4\xd0\xb8\xd0\xbd\xd0\xb0\xd0\xbb\xd1\x8c\xd0\xbd\xd1\x8b\xd0\xb9 \xd1\x81\xd1\x82\xd0\xb0\xd1\x82\xd1\x83\xd1\x81', choices=[(b'pass', b'Pass'), (b'fail', b'Fail'), (b'dbg', b'Debug'), (b'unk', b'Unknown')]),
            preserve_default=True,
        ),
    ]
