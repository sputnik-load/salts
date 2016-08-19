# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_pgjsonb.fields


class Migration(migrations.Migration):

    dependencies = [
        ('salts', '0033_auto_20160713_1236'),
    ]

    operations = [
        migrations.AddField(
            model_name='shooting',
            name='custom_data',
            field=django_pgjsonb.fields.JSONField(default={}, null=True, encode_kwargs={}, decode_kwargs={}),
        ),
    ]
