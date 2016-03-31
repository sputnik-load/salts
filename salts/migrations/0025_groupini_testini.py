# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salts', '0024_auto_20160202_1245'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupIni',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='\u0418\u043c\u044f \u0433\u0440\u0443\u043f\u043f\u044b', max_length=256, null=True, verbose_name='\u0418\u043c\u044f \u0433\u0440\u0443\u043f\u043f\u044b', blank=True)),
                ('codename', models.CharField(help_text='\u0418\u043c\u044f \u0433\u0440\u0443\u043f\u043f\u044b \u043d\u0430 \u0430\u043d\u0433\u043b\u0438\u0439\u0441\u043a\u043e\u043c', max_length=256, null=True, verbose_name='\u041a\u043e\u0440\u043e\u0442\u043a\u0438\u0439 \u0438\u0434\u0435\u043d\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u043e\u0440 \u0433\u0440\u0443\u043f\u043f\u044b', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='TestIni',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('scenario_id', models.CharField(help_text='\u041e\u0442\u043d\u043e\u0441\u0438\u0442\u0435\u043b\u044c\u043d\u044b\u0439 \u043f\u0443\u0442\u044c \u043a \u0441\u0446\u0435\u043d\u0430\u0440\u0438\u044e \u0432\u043d\u0443\u0442\u0440\u0438 \u0440\u0435\u043f\u043e\u0437\u0438\u0442\u043e\u0440\u0438\u044f', max_length=256, null=True, verbose_name='Id \u0441\u0446\u0435\u043d\u0430\u0440\u0438\u044f', blank=True)),
                ('group_ini', models.ForeignKey(to='salts.GroupIni')),
            ],
        ),
    ]
