# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salts', '0014_testrun'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testrun',
            name='status',
            field=models.CharField(default=b'run', help_text=b'\xd0\xa4\xd0\xb8\xd0\xbd\xd0\xb0\xd0\xbb\xd1\x8c\xd0\xbd\xd1\x8b\xd0\xb9 \xd1\x81\xd1\x82\xd0\xb0\xd1\x82\xd1\x83\xd1\x81 \xd1\x82\xd0\xb5\xd1\x81\xd1\x82\xd0\xb0 - Pass \xd0\xb8\xd0\xbb\xd0\xb8 Fail.', max_length=4, verbose_name=b'\xd0\xa1\xd1\x82\xd0\xb0\xd1\x82\xd1\x83\xd1\x81', choices=[(b'upl', b'Uploading'), (b'upld', b'Uploaded'), (b'pre', b'Prepare'), (b'run', b'Running'), (b'arc', b'Archiving'), (b'stor', b'Storing'), (b'done', b'Done'), (b'unk', b'Unknown')]),
        ),
    ]
