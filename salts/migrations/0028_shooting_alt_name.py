# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salts', '0027_auto_20160520_1924'),
    ]

    operations = [
        migrations.AddField(
            model_name='shooting',
            name='alt_name',
            field=models.CharField(help_text='\u041d\u0443\u0436\u043d\u043e, \u0435\u0441\u043b\u0438 \u043d\u0435 \u0443\u043a\u0430\u0437\u0430\u043d \u0442\u043e\u043a\u0435\u043d \u0438 \u0442\u0435\u0441\u0442 \u0437\u0430\u043f\u0443\u0441\u043a\u0430\u0435\u0442\u0441\u044f \u0432 \u043a\u043e\u043d\u0441\u043e\u043b\u0438', max_length=128, null=True, verbose_name='\u0418\u043c\u044f \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f', blank=True),
        ),
    ]
