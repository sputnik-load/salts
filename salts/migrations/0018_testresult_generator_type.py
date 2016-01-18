# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salts', '0017_generatortype'),
    ]

    operations = [
        migrations.AddField(
            model_name='testresult',
            name='generator_type',
            field=models.ForeignKey(default=1, to='salts.GeneratorType'),
        ),
    ]
