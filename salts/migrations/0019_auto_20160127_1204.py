# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('salts', '0018_testresult_generator_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generator',
            name='host',
            field=models.CharField(help_text='\u0421\u0435\u0440\u0432\u0435\u0440 \u043d\u0430\u0433\u0440\u0443\u0437\u043a\u0438', max_length=128, null=True, verbose_name='\u0425\u043e\u0441\u0442', blank=True),
        ),
        migrations.AlterField(
            model_name='generator',
            name='port',
            field=models.IntegerField(help_text='\u041f\u043e\u0440\u0442', null=True, verbose_name='\u041f\u043e\u0440\u0442', blank=True),
        ),
        migrations.AlterField(
            model_name='generator',
            name='tool',
            field=models.CharField(help_text='\u0418\u043d\u0441\u0442\u0440\u0443\u043c\u0435\u043d\u0442 \u0433\u0435\u043d\u0435\u0440\u0430\u0446\u0438\u0438', max_length=128, null=True, verbose_name='\u0413\u0435\u043d\u0435\u0440\u0430\u0442\u043e\u0440', blank=True),
        ),
        migrations.AlterField(
            model_name='generatortype',
            name='name_list',
            field=models.CharField(help_text='\u0421\u043f\u0438\u0441\u043e\u043a \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0435\u043c\u044b\u0445 \u0433\u0435\u043d\u0435\u0440\u0430\u0442\u043e\u0440\u043e\u0432', max_length=255, verbose_name='\u0421\u043f\u0438\u0441\u043e\u043a \u0438\u043c\u0435\u043d \u0433\u0435\u043d\u0435\u0440\u0430\u0442\u043e\u0440\u043e\u0432'),
        ),
        migrations.AlterField(
            model_name='rps',
            name='rps_name',
            field=models.CharField(default=b'0', max_length=32, blank=True, help_text='\u0418\u043c\u044f \u0441\u0445\u0435\u043c\u044b', null=True, verbose_name='\u0418\u043c\u044f \u0441\u0445\u0435\u043c\u044b'),
        ),
        migrations.AlterField(
            model_name='rps',
            name='schedule',
            field=models.CharField(help_text='\u0421\u0445\u0435\u043c\u0430 \u043d\u0430\u0433\u0440\u0443\u0437\u043a\u0438', max_length=256, null=True, verbose_name='\u0421\u0445\u0435\u043c\u0430 \u043d\u0430\u0433\u0440\u0443\u0437\u043a\u0438', blank=True),
        ),
        migrations.AlterField(
            model_name='target',
            name='host',
            field=models.CharField(help_text='\u0425\u043e\u0441\u0442', max_length=128, null=True, verbose_name='\u0425\u043e\u0441\u0442', blank=True),
        ),
        migrations.AlterField(
            model_name='target',
            name='port',
            field=models.IntegerField(help_text='\u041f\u043e\u0440\u0442', null=True, verbose_name='\u041f\u043e\u0440\u0442', blank=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='comments',
            field=models.CharField(help_text=b'', max_length=256, null=True, verbose_name='\u041a\u043e\u043c\u043c\u0435\u043d\u0442\u0430\u0440\u0438\u0438', blank=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='console_log',
            field=models.FileField(upload_to=b'results/%Y/%m/%d', null=True, verbose_name='\u041b\u043e\u0433 \u043a\u043e\u043d\u0441\u043e\u043b\u0438', blank=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='dt_finish',
            field=models.DateTimeField(null=True, verbose_name='\u0414\u0430\u0442\u0430 \u0438 \u0432\u0440\u0435\u043c\u044f \u0437\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u0438\u044f \u0442\u0435\u0441\u0442\u0430', blank=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='dt_start',
            field=models.DateTimeField(null=True, verbose_name='\u0414\u0430\u0442\u0430 \u0438 \u0432\u0440\u0435\u043c\u044f \u043d\u0430\u0447\u0430\u043b\u0430 \u0442\u0435\u0441\u0442\u0430', blank=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='generator',
            field=models.CharField(help_text='\u0441\u0435\u0440\u0432\u0435\u0440 \u0433\u0435\u043d\u0435\u0440\u0430\u0442\u043e\u0440 \u043d\u0430\u0433\u0440\u0443\u0437\u043a\u0438', max_length=128, null=True, verbose_name='\u0413\u0435\u043d\u0435\u0440\u0430\u0442\u043e\u0440', blank=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='graph_url',
            field=models.CharField(help_text='html \u0441\u0441\u044b\u043b\u043a\u0438 \u043d\u0430 \u0433\u0440\u0430\u0444\u0438\u043a\u0438', max_length=256, null=True, verbose_name='\u0413\u0440\u0430\u0444\u0438\u043a\u0438', blank=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='group',
            field=models.CharField(help_text='\u041f\u0440\u043e\u0434\u0443\u043a\u0442 \u043a \u043a\u043e\u0442\u043e\u0440\u043e\u043c\u0443 \u043e\u0442\u043d\u043e\u0441\u0438\u0442\u0441\u044f \u0442\u0435\u0441\u0442', max_length=32, null=True, verbose_name='\u041f\u0440\u043e\u0434\u0443\u043a\u0442', blank=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='http_errors_perc',
            field=models.FloatField(help_text=b'', null=True, verbose_name='http-\u043e\u0448\u0438\u0431\u043a\u0438', blank=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='jm_jtl',
            field=models.FileField(upload_to=b'results/%Y/%m/%d', null=True, verbose_name='jtl (\u0441\u044b\u0440\u044b\u0435 \u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442\u044b jmeter)', blank=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='jm_log',
            field=models.FileField(upload_to=b'results/%Y/%m/%d', null=True, verbose_name='\u041b\u043e\u0433 jmeter', blank=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='jm_log_2',
            field=models.FileField(upload_to=b'results/%Y/%m/%d', null=True, verbose_name='\u0414\u043e\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c\u043d\u044b\u0439 \u043b\u043e\u0433 jmeter (testResults.txt)', blank=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='meta',
            field=jsonfield.fields.JSONCharField(help_text='\u0421\u043b\u0443\u0436\u0435\u0431\u043d\u0430\u044f \u0438\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f - \u043d\u0435 \u0438\u0437\u043c\u0435\u043d\u044f\u0442\u044c.', max_length=1024, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='metrics',
            field=models.FileField(upload_to=b'results/%Y/%m/%d', null=True, verbose_name='\u041c\u0435\u0442\u0440\u0438\u043a\u0438', blank=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='mnt_url',
            field=models.CharField(help_text=b'', max_length=256, null=True, verbose_name='\u041c\u0435\u0442\u043e\u0434\u0438\u043a\u0430 \u041d\u0422', blank=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='net_errors_perc',
            field=models.FloatField(help_text=b'', null=True, verbose_name='net-\u043e\u0448\u0438\u0431\u043a\u0438', blank=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='ph_conf',
            field=models.FileField(upload_to=b'results/%Y/%m/%d', null=True, verbose_name='\u041a\u043e\u043d\u0444\u0438\u0433 phantom', blank=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='phout',
            field=models.FileField(upload_to=b'results/%Y/%m/%d', null=True, verbose_name='phout (\u0441\u044b\u0440\u044b\u0435 \u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442\u044b phantom)', blank=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='report_txt',
            field=models.FileField(upload_to=b'results/%Y/%m/%d', null=True, verbose_name='\u0422\u0435\u043a\u0441\u0442\u043e\u0432\u044b\u0439 \u043e\u0442\u0447\u0435\u0442 SputnikReport', blank=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='rps',
            field=models.CharField(help_text='\u041f\u043e\u0434\u0430\u0432\u0430\u0435\u043c\u0430\u044f \u043d\u0430\u0433\u0440\u0443\u0437\u043a\u0430', max_length=128, null=True, verbose_name=b'RPS', blank=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='scenario_id',
            field=models.CharField(default=b'unknown', help_text='\u041f\u0443\u0442\u044c \u043a \u0444\u0430\u0439\u043b\u0443 \u0432 \u0440\u0435\u043f\u043e\u0437\u0438\u0442\u043e\u0440\u0438\u0438', max_length=256, verbose_name='ID \u0441\u0446\u0435\u043d\u0430\u0440\u0438\u044f'),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='target',
            field=models.CharField(help_text='\u041d\u0430\u0433\u0440\u0443\u0436\u0430\u0435\u043c\u0430\u044f \u0441\u0438\u0441\u0442\u0435\u043c\u0430', max_length=128, null=True, verbose_name='Target', blank=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='test_id',
            field=models.CharField(null=True, max_length=32, blank=True, help_text='ID \u0442\u0435\u0441\u0442\u0430', unique=True, verbose_name='ID \u0442\u0435\u0441\u0442\u0430'),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='test_name',
            field=models.CharField(help_text='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0442\u0435\u0441\u0442\u0430', max_length=128, null=True, verbose_name='\u0422\u0435\u0441\u0442', blank=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='test_status',
            field=models.CharField(default=b'unk', help_text='\u0424\u0438\u043d\u0430\u043b\u044c\u043d\u044b\u0439 \u0441\u0442\u0430\u0442\u0443\u0441 \u0442\u0435\u0441\u0442\u0430 - Pass \u0438\u043b\u0438 Fail.', max_length=4, verbose_name='\u0424\u0438\u043d\u0430\u043b\u044c\u043d\u044b\u0439 \u0441\u0442\u0430\u0442\u0443\u0441', choices=[(b'pass', b'Pass'), (b'fail', b'Fail'), (b'dbg', b'Debug'), (b'unk', b'Unknown')]),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='ticket_id',
            field=models.CharField(help_text=b'', max_length=64, null=True, verbose_name='\u0422\u0438\u043a\u0435\u0442', blank=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='user',
            field=models.CharField(help_text='\u043a\u0442\u043e \u0437\u0430\u043f\u0443\u0441\u043a\u0430\u043b \u0442\u0435\u0441\u0442', max_length=128, null=True, verbose_name=b'SPE', blank=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='version',
            field=models.CharField(help_text='\u0412\u0435\u0440\u0441\u0438\u044f \u0441\u0438\u0441\u0442\u0435\u043c\u044b', max_length=128, null=True, verbose_name='\u0412\u0435\u0440\u0441\u0438\u044f', blank=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='yt_conf',
            field=models.FileField(upload_to=b'results/%Y/%m/%d', null=True, verbose_name='\u041a\u043e\u043d\u0444\u0438\u0433 yandex-tank', blank=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='yt_log',
            field=models.FileField(upload_to=b'results/%Y/%m/%d', null=True, verbose_name='\u041b\u043e\u0433 yandex-tank', blank=True),
        ),
        migrations.AlterField(
            model_name='testrun',
            name='datetime',
            field=models.DateTimeField(auto_now=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u0437\u0430\u043f\u0443\u0441\u043a\u0430'),
        ),
        migrations.AlterField(
            model_name='testrun',
            name='status',
            field=models.CharField(default=b'run', help_text='\u0424\u0438\u043d\u0430\u043b\u044c\u043d\u044b\u0439 \u0441\u0442\u0430\u0442\u0443\u0441 \u0442\u0435\u0441\u0442\u0430 - Pass \u0438\u043b\u0438 Fail.', max_length=4, verbose_name='\u0421\u0442\u0430\u0442\u0443\u0441', choices=[(b'upl', b'Uploading'), (b'upld', b'Uploaded'), (b'pre', b'Prepare'), (b'run', b'Running'), (b'arc', b'Archiving'), (b'stor', b'Storing'), (b'done', b'Done'), (b'unk', b'Unknown')]),
        ),
        migrations.AlterField(
            model_name='testsettings',
            name='file_path',
            field=models.CharField(help_text='\u041f\u0443\u0442\u044c \u043a \u0444\u0430\u0439\u043b\u0443', max_length=128, null=True, verbose_name='\u041f\u0443\u0442\u044c \u043a \u0444\u0430\u0439\u043b\u0443', blank=True),
        ),
        migrations.AlterField(
            model_name='testsettings',
            name='test_name',
            field=models.CharField(help_text='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0442\u0435\u0441\u0442\u0430', max_length=512, null=True, verbose_name='\u0422\u0435\u0441\u0442', blank=True),
        ),
        migrations.AlterField(
            model_name='testsettings',
            name='ticket',
            field=models.CharField(help_text='\u041d\u043e\u043c\u0435\u0440 \u0442\u0438\u043a\u0435\u0442\u0430', max_length=128, null=True, verbose_name='\u0422\u0438\u043a\u0435\u0442', blank=True),
        ),
        migrations.AlterField(
            model_name='testsettings',
            name='version',
            field=models.CharField(help_text='\u041d\u043e\u043c\u0435\u0440 \u0432\u0435\u0440\u0441\u0438\u0438', max_length=128, null=True, verbose_name='\u0412\u0435\u0440\u0441\u0438\u044f', blank=True),
        ),
    ]
