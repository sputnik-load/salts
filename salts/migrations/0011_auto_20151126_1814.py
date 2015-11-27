# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('salts', '0010_testresult_jm_log_2'),
    ]

    operations = [
        migrations.CreateModel(
            name='Generator',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('host', models.CharField(help_text=b'\xd0\xa1\xd0\xb5\xd1\x80\xd0\xb2\xd0\xb5\xd1\x80 \xd0\xbd\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd0\xb8', max_length=128, null=True, verbose_name=b'\xd0\xa5\xd0\xbe\xd1\x81\xd1\x82', blank=True)),
                ('port', models.IntegerField(help_text=b'\xd0\x9f\xd0\xbe\xd1\x80\xd1\x82', max_length=128, null=True, verbose_name=b'\xd0\x9f\xd0\xbe\xd1\x80\xd1\x82', blank=True)),
                ('tool', models.CharField(help_text=b'\xd0\x98\xd0\xbd\xd1\x81\xd1\x82\xd1\x80\xd1\x83\xd0\xbc\xd0\xb5\xd0\xbd\xd1\x82 \xd0\xb3\xd0\xb5\xd0\xbd\xd0\xb5\xd1\x80\xd0\xb0\xd1\x86\xd0\xb8\xd0\xb8', max_length=128, null=True, verbose_name=b'\xd0\x93\xd0\xb5\xd0\xbd\xd0\xb5\xd1\x80\xd0\xb0\xd1\x82\xd0\xbe\xd1\x80', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RPS',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rps_name', models.CharField(default=b'0', max_length=32, blank=True, help_text=b'\xd0\x98\xd0\xbc\xd1\x8f \xd1\x81\xd1\x85\xd0\xb5\xd0\xbc\xd1\x8b', null=True, verbose_name=b'\xd0\x98\xd0\xbc\xd1\x8f \xd1\x81\xd1\x85\xd0\xb5\xd0\xbc\xd1\x8b')),
                ('schedule', models.CharField(help_text=b'\xd0\xa1\xd1\x85\xd0\xb5\xd0\xbc\xd0\xb0 \xd0\xbd\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd0\xb8', max_length=256, null=True, verbose_name=b'\xd0\xa1\xd1\x85\xd0\xb5\xd0\xbc\xd0\xb0 \xd0\xbd\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd0\xb8', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Target',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('host', models.CharField(help_text=b'\xd0\xa5\xd0\xbe\xd1\x81\xd1\x82', max_length=128, null=True, verbose_name=b'\xd0\xa5\xd0\xbe\xd1\x81\xd1\x82', blank=True)),
                ('port', models.IntegerField(help_text=b'\xd0\x9f\xd0\xbe\xd1\x80\xd1\x82', null=True, verbose_name=b'\xd0\x9f\xd0\xbe\xd1\x80\xd1\x82', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TestSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file_path', models.CharField(help_text=b'\xd0\x9f\xd1\x83\xd1\x82\xd1\x8c \xd0\xba \xd1\x84\xd0\xb0\xd0\xb9\xd0\xbb\xd1\x83', max_length=128, null=True, verbose_name=b'\xd0\x9f\xd1\x83\xd1\x82\xd1\x8c \xd0\xba \xd1\x84\xd0\xb0\xd0\xb9\xd0\xbb\xd1\x83', blank=True)),
                ('test_name', models.CharField(help_text=b'\xd0\x9d\xd0\xb0\xd0\xb7\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5 \xd1\x82\xd0\xb5\xd1\x81\xd1\x82\xd0\xb0', max_length=128, null=True, verbose_name=b'\xd0\xa2\xd0\xb5\xd1\x81\xd1\x82', blank=True)),
                ('ticket', models.CharField(help_text=b'\xd0\x9d\xd0\xbe\xd0\xbc\xd0\xb5\xd1\x80 \xd1\x82\xd0\xb8\xd0\xba\xd0\xb5\xd1\x82\xd0\xb0', max_length=128, null=True, verbose_name=b'\xd0\xa2\xd0\xb8\xd0\xba\xd0\xb5\xd1\x82', blank=True)),
                ('version', models.CharField(help_text=b'\xd0\x9d\xd0\xbe\xd0\xbc\xd0\xb5\xd1\x80 \xd0\xb2\xd0\xb5\xd1\x80\xd1\x81\xd0\xb8\xd0\xb8', max_length=128, null=True, verbose_name=b'\xd0\x92\xd0\xb5\xd1\x80\xd1\x81\xd0\xb8\xd1\x8f', blank=True)),
                ('generator', models.ForeignKey(to='salts.Generator')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='rps',
            name='target',
            field=models.ForeignKey(to='salts.Target'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='rps',
            name='test_settings',
            field=models.ForeignKey(to='salts.TestSettings'),
            preserve_default=True,
        ),
    ]
