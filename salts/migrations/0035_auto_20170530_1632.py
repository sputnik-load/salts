# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salts', '0034_shooting_custom_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scenario',
            name='status',
            field=models.CharField(default=b'S', help_text='\u0421\u0442\u0430\u0442\u0443\u0441 \u0441\u0446\u0435\u043d\u0430\u0440\u0438\u044f - A\u043a\u0442\u0438\u0432\u043d\u044b\u0439 \u0438\u043b\u0438 \u0423\u0434\u0430\u043b\u0435\u043d\u043d\u044b\u0439.', max_length=1, verbose_name='\u0421\u0442\u0430\u0442\u0443\u0441', choices=[(b'A', b'Active'), (b'D', b'Deleled'), (b'S', b'Sleeping')]),
        ),
    ]
