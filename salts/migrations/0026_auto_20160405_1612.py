# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salts', '0025_groupini_testini'),
    ]

    operations = [
        migrations.RunSQL("""INSERT INTO salts_groupini (id, name, codename)
                             VALUES (1, 'Неизвестно', 'unknown')
                          """),
    ]
