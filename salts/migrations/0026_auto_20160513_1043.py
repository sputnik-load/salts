# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salts', '0025_auto_20160504_1951'),
    ]

    operations = [
        migrations.AddField(
            model_name='shooting',
            name='start',
            field=models.IntegerField(null=True, verbose_name='\u041e\u0442\u043c\u0435\u0442\u043a\u0430 \u0432\u0440\u0435\u043c\u0435\u043d\u0438 \u043d\u0430\u0447\u0430\u043b\u0430 \u0441\u0442\u0440\u0435\u043b\u044c\u0431\u044b', blank=True),
        ),
        migrations.AddField(
            model_name='shooting',
            name='finish',
            field=models.IntegerField(null=True, verbose_name='\u041e\u0442\u043c\u0435\u0442\u043a\u0430 \u0432\u0440\u0435\u043c\u0435\u043d\u0438 \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f \u0441\u0442\u0440\u0435\u043b\u044c\u0431\u044b', blank=True),
        ),
        migrations.AddField(
            model_name='shooting',
            name='planned_duration',
            field=models.IntegerField(null=True, verbose_name='\u041f\u043b\u0430\u043d\u0438\u0440\u0443\u0435\u043c\u0430\u044f \u0434\u043b\u0438\u0442\u0435\u043b\u044c\u043d\u043e\u0441\u0442\u044c \u0442\u0435\u0441\u0442\u0430', blank=True),
        ),
        migrations.RunSQL("""UPDATE salts_shooting
                             SET start=EXTRACT(epoch FROM dt_start),
                                 finish=EXTRACT(epoch FROM dt_finish)
                          """),
    ]
