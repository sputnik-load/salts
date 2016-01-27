# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salts', '0021_auto_20160127_1222'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeneratorType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='\u0418\u043c\u044f \u0433\u0435\u043d\u0435\u0440\u0430\u0442\u043e\u0440\u0430', max_length=255, verbose_name='\u0418\u043c\u044f \u0433\u0435\u043d\u0435\u0440\u0430\u0442\u043e\u0440\u0430')),
            ],
        ),
        migrations.AddField(
            model_name='testresult',
            name='generator_types',
            field=models.ManyToManyField(to='salts.GeneratorType'),
        ),
    ]
