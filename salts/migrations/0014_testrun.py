# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salts', '0013_auto_20151127_1158'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestRun',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime', models.DateTimeField(auto_now=True, verbose_name=b'\xd0\x92\xd1\x80\xd0\xb5\xd0\xbc\xd1\x8f \xd0\xb7\xd0\xb0\xd0\xbf\xd1\x83\xd1\x81\xd0\xba\xd0\xb0')),
                ('status', models.CharField(default=b'pre', help_text=b'\xd0\xa4\xd0\xb8\xd0\xbd\xd0\xb0\xd0\xbb\xd1\x8c\xd0\xbd\xd1\x8b\xd0\xb9 \xd1\x81\xd1\x82\xd0\xb0\xd1\x82\xd1\x83\xd1\x81 \xd1\x82\xd0\xb5\xd1\x81\xd1\x82\xd0\xb0 - Pass \xd0\xb8\xd0\xbb\xd0\xb8 Fail.', max_length=4, verbose_name=b'\xd0\xa1\xd1\x82\xd0\xb0\xd1\x82\xd1\x83\xd1\x81', choices=[(b'upl', b'Uploading'), (b'upld', b'Uploaded'), (b'pre', b'Prepare'), (b'run', b'Running'), (b'arc', b'Archiving'), (b'stor', b'Storing'), (b'done', b'Done'), (b'unk', b'Unknown')])),
                ('generator', models.ForeignKey(to='salts.Generator')),
                ('test_settings', models.ForeignKey(to='salts.TestSettings')),
            ],
        ),
    ]
