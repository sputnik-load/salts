# -*- coding: utf-8 -*-
from django.db import models
import logging
from jsonfield import JSONCharField
#from test.test_threading_local import target
from _bsddb import version

# Create your models here.
class TestResult(models.Model):
    """
    Результаты теста
    """
    logger = logging.getLogger(__name__)
    TEST_STATUS_PASS = 'pass'
    TEST_STATUS_FAIL = 'fail'
    TEST_STATUS_DEBUG = 'dbg'
    STATUS_UPLOADING = 'upl'
    STATUS_UPLOADED = 'upld'
    STATUS_PREPARE = 'pre'
    STATUS_RUNNING = 'run'
    STATUS_ARCHIVING = 'arc'
    STATUS_STORING = 'stor'
    STATUS_UNKNOWN = 'unk'
    STATUS_DONE = 'done'
    TEST_STATUS_CHOICES = (
        (TEST_STATUS_PASS, 'Pass'),
        (TEST_STATUS_FAIL, 'Fail'),
        (TEST_STATUS_DEBUG, 'Debug'),
        (STATUS_UNKNOWN, 'Unknown'),
    )
    STATUS_CHOICES = (
        (STATUS_UPLOADING, 'Uploading'),
        (STATUS_UPLOADED, 'Uploaded'),
        (STATUS_PREPARE, 'Prepare'),
        (STATUS_RUNNING, 'Running'),
        (STATUS_ARCHIVING, 'Archiving'),
        (STATUS_STORING, 'Storing'),
        (STATUS_DONE, 'Done'),
        (STATUS_UNKNOWN, 'Unknown'),
    )
    test_id = models.CharField('ID', max_length=32, help_text='ID теста', null=True, blank=True, unique=True)
    dt_start = models.DateTimeField('Дата и время начала теста', null=True, blank=True)
    dt_finish = models.DateTimeField('Дата и время завершения теста', null=True, blank=True)
    group = models.CharField('Продукт', max_length=32, help_text='Продукт к которому относится тест', null=True, blank=True)
    test_name = models.CharField('Тест', max_length=128, help_text='Название теста', null=True, blank=True)
    target =  models.CharField('Target', max_length=128, help_text='Нагружаемая система', null=True, blank=True)
    version = models.CharField('Версия', max_length=128, help_text='Версия системы', null=True, blank=True)
    rps = models.CharField('RPS', max_length=128, help_text='Подаваемая нагрузка', null=True, blank=True)
    q99 = models.FloatField('99%', help_text='Квантиль 99%', null=True, blank=True)
    q90 = models.FloatField('90%', help_text='Квантиль 90%', null=True, blank=True)
    q50 = models.FloatField('50%', help_text='Квантиль 50%', null=True, blank=True)
    http_errors_perc = models.FloatField('http-ошибки', help_text='', null=True, blank=True)
    net_errors_perc = models.FloatField('net-ошибки', help_text='', null=True, blank=True)
    # length
    graph_url = models.CharField('Графики', max_length=256, help_text='html ссылки на графики', null=True, blank=True)
    generator = models.CharField('Генератор', max_length=128, help_text='сервер генератор нагрузки', null=True, blank=True)
    user = models.CharField('SPE', max_length=128, help_text='кто запускал тест', null=True, blank=True)
    ticket_id = models.CharField('Тикет', max_length=64, help_text='', null=True, blank=True)
    mnt_url = models.CharField('Методика НТ', max_length=256, help_text='', null=True, blank=True)
    comments = models.CharField('Комментарии', max_length=256, help_text='', null=True, blank=True)
#    dt_start2 = models.DateTimeField(help_text='Дата и время начала теста (зачетный период)', null=True, blank=True)
#    dt_finish2 = models.DateTimeField(help_text='Дата и время завершения теста (зачетный период)', null=True,
#                                      blank=True)
    
    
#     status = models.CharField('Статус выполнения', max_length=4, choices=STATUS_CHOICES, default=STATUS_UNKNOWN,
#                               help_text='Статус выполнения теста: Uploading -> Uploaded -> [Prepare]* -> Running -> ' +
#                                         'Archiving -> Storing -> Done</br>\n' +
#                                         '* - в скобках опциональный статус (может быть пропущен).')
    test_status = models.CharField('Финальный статус', max_length=4, choices=TEST_STATUS_CHOICES,
                                   default=STATUS_UNKNOWN,
                                   help_text='Финальный статус теста - Pass или Fail.')
#    test_scenario = models.ForeignKey(TestScenario)
#     results = models.FileField('Архив с результатами работы СНТ', upload_to='results/%Y/%m/%d', null=True,
#                                blank=True)
#    ltt_server = models.ForeignKey(Server, verbose_name='Нагрузочный сервер', null=True)
#    environment_config = models.ForeignKey(EnvironmentConfig, null=True)
    metrics = models.FileField('Метрики', upload_to='results/%Y/%m/%d', null=True, blank=True)
    jm_jtl = models.FileField('jtl (сырые результаты jmeter)', upload_to='results/%Y/%m/%d', null=True, blank=True)
    phout = models.FileField('phout (сырые результаты phantom)', upload_to='results/%Y/%m/%d', null=True, blank=True)
    yt_log = models.FileField('Лог yandex-tank', upload_to='results/%Y/%m/%d', null=True, blank=True)
    jm_log = models.FileField('Лог jmeter', upload_to='results/%Y/%m/%d', null=True, blank=True)
    yt_conf = models.FileField('Конфиг yandex-tank', upload_to='results/%Y/%m/%d', null=True, blank=True)
    ph_conf = models.FileField('Конфиг phantom', upload_to='results/%Y/%m/%d', null=True, blank=True)
    modified_jmx = models.FileField('modified.jmx', upload_to='results/%Y/%m/%d', null=True, blank=True)
    console_log = models.FileField('Лог консоли', upload_to='results/%Y/%m/%d', null=True, blank=True)
    report_txt = models.FileField('Текстовый отчет SputnikReport', upload_to='results/%Y/%m/%d', null=True, blank=True)
    jm_log_2 = models.FileField('Дополнительный лог jmeter (testResults.txt)', upload_to='results/%Y/%m/%d', null=True, blank=True)
    meta = JSONCharField(max_length=1024, null=True, blank=True, help_text='Служебная информация - не изменять.')

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.group + '.' + self.test_name + ' ' + self.version + ' ' + self.test_id
    
    def get_name(self):  # Python 3: def __str__(self):
        return self.group + '.' + self.test_name #+ ' ' + self.version + ' ' + self.test_id