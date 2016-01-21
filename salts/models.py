# -*- coding: utf-8 -*-
from django.db import models
import logging
from jsonfield import JSONCharField
#from test.test_threading_local import target
from _bsddb import version

# Create your models here.
class GeneratorType(models.Model):
    name_list = models.CharField('Список имен генераторов', max_length=255,
                                 help_text='Список используемых генераторов',
                                 null=False, blank=False)

    def __unicode__(self):
        return self.name_list


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
    test_id = models.CharField('ID теста', max_length=32, help_text='ID теста', null=True, blank=True, unique=True)
    scenario_id = models.CharField('ID сценария', max_length=256, help_text='Путь к файлу в репозитории', null=False, default='unknown')
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
    generator_type = models.ForeignKey(GeneratorType, default=1, null=False, blank=False)
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


class Generator(models.Model):
    host = models.CharField('Хост', max_length=128,
                            help_text='Сервер нагрузки',
                            null=True, blank=True)
    port = models.IntegerField('Порт',
                               help_text='Порт',
                               null=True, blank=True)
    tool = models.CharField('Генератор', max_length=128,
                            help_text='Инструмент генерации',
                            null=True, blank=True)

    def __unicode__(self):
        return "%s:%s (%s)" % (self.host, self.port, self.tool)


class Target(models.Model):
    host = models.CharField('Хост', max_length=128,
                            help_text='Хост',
                            null=True, blank=True)
    port = models.IntegerField('Порт',
                               help_text='Порт',
                               null=True, blank=True)

    def __unicode__(self):
        return "%s:%s" % (self.host, self.port)

class TestSettings(models.Model):
    file_path = models.CharField('Путь к файлу', max_length=128,
                                 help_text='Путь к файлу',
                                 null=True, blank=True)
    test_name = models.CharField('Тест', max_length=512,
                                 help_text='Название теста',
                                 null=True, blank=True)
    generator = models.ForeignKey(Generator)
    ticket = models.CharField('Тикет', max_length=128,
                              help_text='Номер тикета',
                              null=True, blank=True)
    version = models.CharField('Версия', max_length=128,
                               help_text='Номер версии',
                               null=True, blank=True)

    def __unicode__(self):
        return "%s (%s)" % (self.test_name, self.ticket)


class RPS(models.Model):
    test_settings = models.ForeignKey(TestSettings)
    rps_name = models.CharField('Имя схемы', max_length=32,
                                help_text='Имя схемы',
                                default='0',
                                null=True, blank=True)
    schedule = models.CharField('Схема нагрузки', max_length=256,
                                   help_text='Схема нагрузки',
                                   null=True, blank=True)
    target = models.ForeignKey(Target)
    def __unicode__(self):
        return "%s: %s" % (self.rps_name, self.schedule)


class TestRun(models.Model):
    STATUS_UPLOADING = 'upl'
    STATUS_UPLOADED = 'upld'
    STATUS_PREPARE = 'pre'
    STATUS_RUNNING = 'run'
    STATUS_ARCHIVING = 'arc'
    STATUS_STORING = 'stor'
    STATUS_UNKNOWN = 'unk'
    STATUS_DONE = 'done'
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

    datetime = models.DateTimeField('Время запуска', auto_now=True)
    test_settings = models.ForeignKey(TestSettings)
    generator = models.ForeignKey(Generator)
    status = models.CharField('Статус', max_length=4,
                              choices=STATUS_CHOICES,
                              default=STATUS_RUNNING,
                              help_text='Финальный статус теста - Pass или Fail.')

    def __unicode__(self):
        return "Id: %s (datetime: %s)." % (self.id, self.datetime)
