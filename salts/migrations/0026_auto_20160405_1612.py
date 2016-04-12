# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salts', '0025_groupini_testini'),
    ]

    operations = [
        migrations.RunSQL(
            ["INSERT INTO salts_groupini (name, codename) VALUES ('Неизвестно', 'unknown')"],
            ["DELETE FROM salts_groupini WHERE codename='unknown'"]
        ),
    ]
