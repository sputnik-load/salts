# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salts', '0015_auto_20151201_1138'),
    ]

    operations = [
        migrations.AddField(
            model_name='testresult',
            name='scenario_id',
            field=models.CharField(default=b'unknown', help_text=b'\xd0\x9f\xd1\x83\xd1\x82\xd1\x8c \xd0\xba \xd1\x84\xd0\xb0\xd0\xb9\xd0\xbb\xd1\x83 \xd0\xb2 \xd1\x80\xd0\xb5\xd0\xbf\xd0\xbe\xd0\xb7\xd0\xb8\xd1\x82\xd0\xbe\xd1\x80\xd0\xb8\xd0\xb8', max_length=256, verbose_name=b'ID \xd1\x81\xd1\x86\xd0\xb5\xd0\xbd\xd0\xb0\xd1\x80\xd0\xb8\xd1\x8f'),
        ),
    ]
