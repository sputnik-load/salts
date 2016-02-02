# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salts', '0023_auto_20160127_1926'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testresult',
            name='comments',
            field=models.TextField(help_text='\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0439 \u043a \u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442\u0430\u043c \u0442\u0435\u0441\u0442\u0430', max_length=1024, null=True, verbose_name='\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0438', blank=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='generator_types',
            field=models.ManyToManyField(related_name='generator_types', to='salts.GeneratorType'),
        ),
    ]
