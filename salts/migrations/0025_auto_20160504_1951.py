# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('salts', '0024_auto_20160202_1245'),
    ]

    operations = [
        migrations.CreateModel(
            name='Shooting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('test_id', models.CharField(null=True, max_length=32, blank=True, help_text='ID \u0442\u0435\u0441\u0442\u0430', unique=True, verbose_name='ID \u0442\u0435\u0441\u0442\u0430')),
                ('dt_start', models.DateTimeField(null=True, verbose_name='\u0414\u0430\u0442\u0430 \u0438 \u0432\u0440\u0435\u043c\u044f \u043d\u0430\u0447\u0430\u043b\u0430 \u0441\u0442\u0440\u0435\u043b\u044c\u0431\u044b', blank=True)),
                ('dt_finish', models.DateTimeField(null=True, verbose_name='\u0414\u0430\u0442\u0430 \u0438 \u0432\u0440\u0435\u043c\u044f \u0437\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u0438\u044f \u0441\u0442\u0440\u0435\u043b\u044c\u0431\u044b', blank=True)),
                ('status', models.CharField(default=b'P', help_text='\u0421\u0442\u0430\u0442\u0443\u0441 \u0441\u0442\u0440\u0435\u043b\u044c\u0431\u044b - \u0413\u043e\u0442\u043e\u0432\u0438\u0442\u0441\u044f, \u0412\u044b\u043f\u043e\u043b\u043d\u044f\u0435\u0442\u0441\u044f, \u0417\u0430\u043a\u043e\u043d\u0447\u0435\u043d \u0438\u043b\u0438 \u041f\u0440\u0435\u0440\u0432\u0430\u043d.', max_length=1, verbose_name='\u0421\u0442\u0430\u0442\u0443\u0441 \u0441\u0442\u0440\u0435\u043b\u044c\u0431\u044b', choices=[(b'P', b'Prepare'), (b'R', b'Running'), (b'F', b'Finished'), (b'I', b'Interrupted')])),
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
        migrations.CreateModel(
            name='TestIni',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('scenario_id', models.CharField(help_text='\u041e\u0442\u043d\u043e\u0441\u0438\u0442\u0435\u043b\u044c\u043d\u044b\u0439 \u043f\u0443\u0442\u044c \u043a \u0441\u0446\u0435\u043d\u0430\u0440\u0438\u044e \u0432\u043d\u0443\u0442\u0440\u0438 \u0440\u0435\u043f\u043e\u0437\u0438\u0442\u043e\u0440\u0438\u044f', max_length=256, null=True, verbose_name='Id \u0441\u0446\u0435\u043d\u0430\u0440\u0438\u044f', blank=True)),
                ('status', models.CharField(default=b'A', help_text='\u0421\u0442\u0430\u0442\u0443\u0441 \u0441\u0446\u0435\u043d\u0430\u0440\u0438\u044f - A\u043a\u0442\u0438\u0432\u043d\u044b\u0439 \u0438\u043b\u0438 \u0423\u0434\u0430\u043b\u0435\u043d\u043d\u044b\u0439.', max_length=1, verbose_name='\u0421\u0442\u0430\u0442\u0443\u0441', choices=[(b'A', b'Active'), (b'D', b'Deleled')])),
                ('group', models.ForeignKey(to='auth.Group')),
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
