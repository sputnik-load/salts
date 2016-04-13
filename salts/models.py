# -*- coding: utf-8 -*-
from django.db import models
import logging
from jsonfield import JSONCharField
#from test.test_threading_local import target
from _bsddb import version
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

# Create your models here.
class GeneratorTypeList(models.Model):
    name_list = models.CharField(u'Список имен генераторов', max_length=255,
                                 help_text=u'Список используемых генераторов',
                                 null=False, blank=False)

    def __unicode__(self):
        return self.name_list


class GeneratorType(models.Model):
    name = models.CharField(u'Имя генератора', max_length=255,
                            help_text=u'Имя генератора',
                            null=False, blank=False)

    def __unicode__(self):
        return self.name


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
    test_id = models.CharField(u'ID теста', max_length=32, help_text=u'ID теста', null=True, blank=True, unique=True)
    scenario_id = models.CharField(u'ID сценария', max_length=256, help_text=u'Путь к файлу в репозитории', null=False, default='unknown')
    dt_start = models.DateTimeField(u'Дата и время начала теста', null=True, blank=True)
    dt_finish = models.DateTimeField(u'Дата и время завершения теста', null=True, blank=True)
    group = models.CharField(u'Продукт', max_length=32, help_text=u'Продукт к которому относится тест', null=True, blank=True)
    test_name = models.CharField(u'Тест', max_length=128, help_text=u'Название теста', null=True, blank=True)
    target =  models.CharField(u'Target', max_length=128, help_text=u'Нагружаемая система', null=True, blank=True)
    version = models.CharField(u'Версия', max_length=128, help_text=u'Версия системы', null=True, blank=True)
    rps = models.CharField('RPS', max_length=128, help_text=u'Подаваемая нагрузка', null=True, blank=True)
    q99 = models.FloatField('99%', help_text='Квантиль 99%', null=True, blank=True)
    q90 = models.FloatField('90%', help_text='Квантиль 90%', null=True, blank=True)
    q50 = models.FloatField('50%', help_text='Квантиль 50%', null=True, blank=True)
    http_errors_perc = models.FloatField(u'http-ошибки', help_text='', null=True, blank=True)
    net_errors_perc = models.FloatField(u'net-ошибки', help_text='', null=True, blank=True)
    # length
    graph_url = models.CharField(u'Графики', max_length=256, help_text=u'html ссылки на графики', null=True, blank=True)
    generator = models.CharField(u'Генератор', max_length=128, help_text=u'сервер генератор нагрузки', null=True, blank=True)
    generator_type_list = models.ForeignKey(GeneratorTypeList, default=1, null=False, blank=False)
    generator_types = models.ManyToManyField(GeneratorType, related_name='generator_types')
    user = models.CharField('SPE', max_length=128, help_text=u'кто запускал тест', null=True, blank=True)
    ticket_id = models.CharField(u'Тикет', max_length=64, help_text='', null=True, blank=True)
    mnt_url = models.CharField(u'Методика НТ', max_length=256, help_text='', null=True, blank=True)
    comments = models.TextField(u'Комментарии', max_length=1024, help_text=u'Комментарий к результатам теста', null=True, blank=True)
#    dt_start2 = models.DateTimeField(help_text='Дата и время начала теста (зачетный период)', null=True, blank=True)
#    dt_finish2 = models.DateTimeField(help_text='Дата и время завершения теста (зачетный период)', null=True,
#                                      blank=True)


#     status = models.CharField('Статус выполнения', max_length=4, choices=STATUS_CHOICES, default=STATUS_UNKNOWN,
#                               help_text='Статус выполнения теста: Uploading -> Uploaded -> [Prepare]* -> Running -> ' +
#                                         'Archiving -> Storing -> Done</br>\n' +
#                                         '* - в скобках опциональный статус (может быть пропущен).')
    test_status = models.CharField(u'Финальный статус', max_length=4, choices=TEST_STATUS_CHOICES,
                                   default=STATUS_UNKNOWN,
                                   help_text=u'Финальный статус теста - Pass или Fail.')
#    test_scenario = models.ForeignKey(TestScenario)
#     results = models.FileField('Архив с результатами работы СНТ', upload_to='results/%Y/%m/%d', null=True,
#                                blank=True)
#    ltt_server = models.ForeignKey(Server, verbose_name='Нагрузочный сервер', null=True)
#    environment_config = models.ForeignKey(EnvironmentConfig, null=True)
    metrics = models.FileField(u'Метрики', upload_to='results/%Y/%m/%d', null=True, blank=True)
    jm_jtl = models.FileField(u'jtl (сырые результаты jmeter)', upload_to='results/%Y/%m/%d', null=True, blank=True)
    phout = models.FileField(u'phout (сырые результаты phantom)', upload_to='results/%Y/%m/%d', null=True, blank=True)
    yt_log = models.FileField(u'Лог yandex-tank', upload_to='results/%Y/%m/%d', null=True, blank=True)
    jm_log = models.FileField(u'Лог jmeter', upload_to='results/%Y/%m/%d', null=True, blank=True)
    yt_conf = models.FileField(u'Конфиг yandex-tank', upload_to='results/%Y/%m/%d', null=True, blank=True)
    ph_conf = models.FileField(u'Конфиг phantom', upload_to='results/%Y/%m/%d', null=True, blank=True)
    modified_jmx = models.FileField('modified.jmx', upload_to='results/%Y/%m/%d', null=True, blank=True)
    console_log = models.FileField(u'Лог консоли', upload_to='results/%Y/%m/%d', null=True, blank=True)
    report_txt = models.FileField(u'Текстовый отчет SputnikReport', upload_to='results/%Y/%m/%d', null=True, blank=True)
    jm_log_2 = models.FileField(u'Дополнительный лог jmeter (testResults.txt)', upload_to='results/%Y/%m/%d', null=True, blank=True)
    meta = JSONCharField(max_length=1024, null=True, blank=True, help_text=u'Служебная информация - не изменять.')

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.group + '.' + self.test_name + ' ' + self.version + ' ' + self.test_id

    def get_name(self):  # Python 3: def __str__(self):
        return self.group + '.' + self.test_name #+ ' ' + self.version + ' ' + self.test_id


class Generator(models.Model):
    host = models.CharField(u'Хост', max_length=128,
                            help_text=u'Сервер нагрузки',
                            null=True, blank=True)
    port = models.IntegerField(u'Порт',
                               help_text=u'Порт',
                               null=True, blank=True)
    tool = models.CharField(u'Генератор', max_length=128,
                            help_text=u'Инструмент генерации',
                            null=True, blank=True)

    def __unicode__(self):
        return "%s:%s (%s)" % (self.host, self.port, self.tool)


class Target(models.Model):
    host = models.CharField(u'Хост', max_length=128,
                            help_text=u'Хост',
                            null=True, blank=True)
    port = models.IntegerField(u'Порт',
                               help_text=u'Порт',
                               null=True, blank=True)

    def __unicode__(self):
        return "%s:%s" % (self.host, self.port)

class TestSettings(models.Model):
    file_path = models.CharField(u'Путь к файлу', max_length=128,
                                 help_text=u'Путь к файлу',
                                 null=True, blank=True)
    test_name = models.CharField(u'Тест', max_length=512,
                                 help_text=u'Название теста',
                                 null=True, blank=True)
    generator = models.ForeignKey(Generator)
    ticket = models.CharField(u'Тикет', max_length=128,
                              help_text=u'Номер тикета',
                              null=True, blank=True)
    version = models.CharField(u'Версия', max_length=128,
                               help_text=u'Номер версии',
                               null=True, blank=True)

    def __unicode__(self):
        return "%s (%s)" % (self.test_name, self.ticket)


class RPS(models.Model):
    test_settings = models.ForeignKey(TestSettings)
    rps_name = models.CharField(u'Имя схемы', max_length=32,
                                help_text=u'Имя схемы',
                                default='0',
                                null=True, blank=True)
    schedule = models.CharField(u'Схема нагрузки', max_length=256,
                                   help_text=u'Схема нагрузки',
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

    datetime = models.DateTimeField(u'Время запуска', auto_now=True)
    test_settings = models.ForeignKey(TestSettings)
    generator = models.ForeignKey(Generator)
    status = models.CharField(u'Статус', max_length=4,
                              choices=STATUS_CHOICES,
                              default=STATUS_RUNNING,
                              help_text=u'Финальный статус теста - Pass или Fail.')

    def __unicode__(self):
        return "Id: %s (datetime: %s)." % (self.id, self.datetime)


class GroupIni(models.Model):
    name = models.CharField(u'Имя группы', max_length=256,
                            help_text=u'Имя группы',
                            null=True, blank=True)
    codename = models.CharField(u'Короткий идентификатор группы', max_length=256,
                            help_text=u'Имя группы на английском',
                            null=True, blank=True)

    def __unicode__(self):
        return self.name

@receiver(post_save, sender=GroupIni)
def add_group_perm(instance, **kwargs):
    content_type = ContentType.objects.get_for_model(GroupIni)
    Permission.objects.create(
        codename="can_edit_%s" % instance.codename,
        name='Can edit test of group "%s"' % instance.name,
        content_type=content_type
    )
    Permission.objects.create(
        codename="can_run_%s" % instance.codename,
        name='Can run test of group "%s"' % instance.name,
        content_type=content_type
    )


@receiver(post_delete, sender=GroupIni)
def delete_group_perm(instance, **kwargs):
    actions = ["edit", "run"]
    for act in actions:
        perm = Permission.objects.get(
                codename="can_%s_%s" % (act, instance.codename)
               )
        perm.delete()


class TestIni(models.Model):
    STATUS_ACTIVE = 'A'
    STATUS_DELETE = 'D'
    STATUS_CHOICES = (
        (STATUS_ACTIVE, 'Active'),
        (STATUS_DELETE, 'Deleled'),
    )
    scenario_id = models.CharField(u'Id сценария', max_length=256,
                                   help_text=u'Относительный путь к сценарию внутри репозитория',
                                   null=True, blank=True)
    status = models.CharField(u'Статус', max_length=1,
                              choices=STATUS_CHOICES,
                              default=STATUS_ACTIVE,
                              help_text=u'Статус сценария - Aктивный или Удаленный.')
    group_ini = models.ForeignKey(GroupIni, null=False, blank=False)

    def __unicode__(self):
        return self.scenario_id
