# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salts', '0028_shooting_alt_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='shooting',
            name='ticket_id',
            field=models.CharField(help_text=b'', max_length=64, null=True, verbose_name='\u0422\u0438\u043a\u0435\u0442 ID', blank=True),
        ),
    ]
