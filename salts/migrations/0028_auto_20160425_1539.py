# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salts', '0027_testini_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Shooting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dt_start', models.DateTimeField(null=True, verbose_name='\u0414\u0430\u0442\u0430 \u0438 \u0432\u0440\u0435\u043c\u044f \u043d\u0430\u0447\u0430\u043b\u0430 \u0441\u0442\u0440\u0435\u043b\u044c\u0431\u044b', blank=True)),
                ('dt_finish', models.DateTimeField(null=True, verbose_name='\u0414\u0430\u0442\u0430 \u0438 \u0432\u0440\u0435\u043c\u044f \u0437\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u0438\u044f \u0441\u0442\u0440\u0435\u043b\u044c\u0431\u044b', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tank',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('host', models.CharField(help_text='\u0425\u043e\u0441\u0442', max_length=128, null=True, verbose_name='\u0425\u043e\u0441\u0442', blank=True)),
                ('port', models.IntegerField(help_text='\u041f\u043e\u0440\u0442', null=True, verbose_name='\u041f\u043e\u0440\u0442', blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='shooting',
            name='tank',
            field=models.ForeignKey(to='salts.Tank'),
        ),
        migrations.AddField(
            model_name='shooting',
            name='test_ini',
            field=models.ForeignKey(to='salts.TestIni'),
        ),
    ]
