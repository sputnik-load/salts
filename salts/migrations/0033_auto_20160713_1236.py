# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salts', '0032_auto_20160713_1213'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scenario',
            name='scenario_path',
            field=models.CharField(help_text='\u041f\u0443\u0442\u044c \u043a ini-\u0444\u0430\u0439\u043b\u0443 \u0432 \u0440\u0435\u043f\u043e\u0437\u0438\u0442\u043e\u0440\u0438\u0438', max_length=256, verbose_name='\u041f\u0443\u0442\u044c \u043a \u0441\u0446\u0435\u043d\u0430\u0440\u0438\u044e', blank=True),
        ),
        migrations.AlterField(
            model_name='shooting',
            name='session_id',
            field=models.CharField(null=True, max_length=32, blank=True, help_text='ID \u0442\u0435\u0441\u0442\u0430', unique=True, verbose_name='ID \u0441\u0435\u0441\u0441\u0438\u0438'),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='scenario_path',
            field=models.CharField(default=b'unknown', help_text='\u041f\u0443\u0442\u044c \u043a ini-\u0444\u0430\u0439\u043b\u0443 \u0432 \u0440\u0435\u043f\u043e\u0437\u0438\u0442\u043e\u0440\u0438\u0438', max_length=256, verbose_name='\u041f\u0443\u0442\u044c \u043a \u0441\u0446\u0435\u043d\u0430\u0440\u0438\u044e'),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='session_id',
            field=models.CharField(null=True, max_length=32, blank=True, help_text='ID \u0442\u0435\u0441\u0442\u0430', unique=True, verbose_name='ID \u0441\u0435\u0441\u0441\u0438\u0438'),
        ),
    ]
