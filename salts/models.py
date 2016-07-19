# -*- coding: utf-8 -*-
from django.db import models
import logging
from jsonfield import JSONCharField
from _bsddb import version
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from tankmanager import tank_manager


logger = logging.getLogger(__name__)


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
    session_id = models.CharField(u"ID сессии", max_length=32,
                                  help_text=u"ID теста", null=True,
                                  blank=True, unique=True)
    scenario_path = models.CharField(u"Путь к сценарию", max_length=256,
                                     help_text=u"Путь к ini-файлу "
                                               u"в репозитории",
                                     null=False, default='unknown')
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
        return self.group + '.' + self.test_name + ' ' \
                + self.version + ' ' + self.session_id

    def get_name(self):  # Python 3: def __str__(self):
        return self.group + '.' + self.test_name


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






class Scenario(models.Model):
    STATUS_ACTIVE = 'A'
    STATUS_DELETE = 'D'
    STATUS_CHOICES = (
        (STATUS_ACTIVE, 'Active'),
        (STATUS_DELETE, 'Deleled'),
    )
    scenario_path = models.CharField(u"Путь к сценарию", max_length=256,
                                     help_text=u"Путь к ini-файлу "
                                               u"в репозитории",
                                     null=False, blank=True)
    status = models.CharField(u'Статус', max_length=1,
                              choices=STATUS_CHOICES,
                              default=STATUS_ACTIVE,
                              help_text=u'Статус сценария - Aктивный или Удаленный.')
    group = models.ForeignKey(Group, null=False, blank=False)

    def __unicode__(self):
        return self.scenario_path


class Tank(models.Model):
    host = models.CharField(u'Хост', max_length=128,
                            help_text=u'Хост',
                            null=True, blank=True)
    port = models.IntegerField(u'Порт',
                               help_text=u'Порт',
                               null=True, blank=True)

    def __unicode__(self):
        return "Tank %s:%s" % (self.host, self.port)


class Shooting(models.Model):
    STATUS_PREPARE = 'P'
    STATUS_RUNNING = 'R'
    STATUS_FINISHED = 'F'
    STATUS_INTERRUPTED = 'I'
    STATUS_CHOICES = (
        (STATUS_PREPARE, 'Prepare'),
        (STATUS_RUNNING, 'Running'),
        (STATUS_FINISHED, 'Finished'),
        (STATUS_INTERRUPTED, 'Interrupted'),
    )

    session_id = models.CharField(u"ID сессии", max_length=32,
                                  help_text=u"ID теста", null=True,
                                  blank=True, unique=True)
    start = models.IntegerField(u"Отметка времени начала стрельбы",
                                null=True, blank=True)
    finish = models.IntegerField(u"Отметка времени окончания стрельбы",
                                 null=True, blank=True)
    planned_duration = models.IntegerField(u"Планируемая длительность теста",
                                           null=True, blank=True)
    scenario = models.ForeignKey(Scenario, null=False, blank=False)
    tank = models.ForeignKey(Tank, null=False, blank=False)
    status = models.CharField(u"Статус стрельбы", max_length=1,
                              choices=STATUS_CHOICES,
                              default=STATUS_PREPARE,
                              help_text=u"Статус стрельбы - Готовится, "
                                        u"Выполняется, Закончен "
                                        u"или Прерван.")
    user = models.ForeignKey(User, null=True, blank=True)
    alt_name = models.CharField(u"Имя пользователя", max_length=128,
                                help_text=u"Нужно, если не указан токен "
                                          u"и тест запускается в консоли",
                                null=True, blank=True)
    ticket_id = models.CharField(u"Тикет ID", max_length=64, help_text='',
                                 null=True, blank=True)

    def __unicode__(self):
        return "Shooting %s" % self.id


@receiver(post_save, sender=Shooting)
def post_save_shooting(instance, **kwargs):
    status_updated = kwargs.get('update_fields') and \
                     'status' in kwargs['update_fields']
    if instance.status == 'I' and (kwargs.get('created') or status_updated):
        tank_manager.interrupt(instance)
    elif instance.status == 'F' and status_updated:
        tank_manager.free(instance.tank.id)
    elif not instance.session_id and kwargs.get('created'):
        tank_manager.start(instance)


@receiver(post_save, sender=Group)
def add_perm(instance, **kwargs):
    perm_codenames = ['add_shooting', 'change_shooting',
                      'add_testresult', 'change_testresult']
    for codename in perm_codenames:
        perm = Permission.objects.get(codename=codename)
        instance.permissions.add(perm)
