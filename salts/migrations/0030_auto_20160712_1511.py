# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salts', '0029_shooting_ticket_id'),
    ]

    operations = [
        migrations.RenameField('TestResult', 'test_id', 'session_id'),
        migrations.RenameField('Shooting', 'test_id', 'session_id')
    ]
