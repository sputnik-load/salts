# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('salts', '0026_auto_20160513_1043'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shooting',
            name='dt_finish',
        ),
        migrations.RemoveField(
            model_name='shooting',
            name='dt_start',
        ),
        migrations.AddField(
            model_name='shooting',
            name='user',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
