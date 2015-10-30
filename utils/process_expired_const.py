# -*- coding: utf-8 -*-
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

TIME_CONFIG_INI = "process_expired.ini"
TC_NO_TOUCH = -1 # Не производить действие с файлом.
DB_SETTINGS_INI = "db_settings.ini"
LOG_FILENAME_DEFAULT = "process_expired.log"

LOGGER_NAME = "process_expired"

SCRIPT_DESC = "Скрипт удаляет или архивирует большие файлы, срок хранения которых в исходном виде истек. Предполагается, что все необходимые конфигурационные файлы лежат вместе со скриптом. Необходимые конфигурационные файлы: файл с настройками времени хранения - process_expired.ini; файл с настройками базы данных - db_settings.ini."
TR_PATH_HELP = "Полный путь к каталогу с файлами. Необходимый параметр."
DB_NAME_HELP = "В конфигурационном файле db_settings.ini имя секции, содержащей настройки для подключения к нужной базе данных."
LOG_FILENAME_HELP = "Полный путь к файлу с логом, включая имя файла."
DRY_RUN_HELP = "Режим, в котором только выводятся сообщения о намерении сделать что-либо с файлами и в базе данных."
VERBOSE_HELP = "Шумный режим: в консоль выводятся все возможные сообщения."
QUIET_HELP = "Тихий режим: в консоль выводятся только предупреждающие сообщения."

TR_PATH_ABSENT_EXC = "Необходимый параметр скрипта path отсутствует. Запусти скрипт с --help."
CONFIG_ABSENT_EXC = "Необходимый конфигурационный файл %s отсутствует. Он должен находиться в том же каталоге, что и запускаемый скрипт."
SECTION_ABSENT_EXC = "Необходимая секция %s отсутствует в конфигурационном файле %s."
OPTION_ABSENT_EXC = "Необходимая опция %s не задана в секции %s в конфигурационном файле %s."
