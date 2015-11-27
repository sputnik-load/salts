# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salts', '0011_auto_20151126_1814'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generator',
            name='port',
            field=models.IntegerField(help_text=b'\xd0\x9f\xd0\xbe\xd1\x80\xd1\x82', null=True, verbose_name=b'\xd0\x9f\xd0\xbe\xd1\x80\xd1\x82', blank=True),
        ),
    ]
