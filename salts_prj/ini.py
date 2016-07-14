# -*- coding: utf-8 -*-

import os
import re
import codecs
from glob import glob
from settings import LT_PATH, EXCLUDE_INI_FILES
from django.db import connection
from django.contrib.auth.models import Group
from salts.models import Scenario
from ConfigParser import ConfigParser, NoSectionError, NoOptionError, Error
from salts.logger import Logger
from salts_prj.settings import LT_PATH, EXCLUDE_INI_FILES


log = Logger.get_logger()


def ini_files(dir_path):
    ini = []
    for root, dirs, files in os.walk(dir_path, topdown=False):
        for name in files:
            full_path = os.path.join(root, name)
            file_name, file_ext = os.path.splitext(full_path)
            if file_ext == '.ini':
                config = ConfigParser()
                try:
                    config.read(full_path)
                except Error, exc:
                    log.warning("Config %s is not valid: %s" %
                                (full_path, exc))
                else:
                    try:
                        test_name = config.get('sputnikreport', 'test_name')
                    except (NoSectionError, NoOptionError):
                        log.info("Config %s is not scenario: "
                                 "there is not 'test_name' option "
                                 "in the 'sputnikreport' section." %
                                 full_path)
                    else:
                        if test_name:
                            ini.append(re.sub("%s/" % dir_path, '', full_path))
                        else:
                            log.warning("Scenario %s contains "
                                        "empty 'test_name' option." %
                                        full_path)
    return ini


class IniDuplicateError(Exception):
    pass

class IniCtrl(object):

    SALTS_SECTION = 'salts'
    REPORT_SECTION = 'sputnikreport'
    DEFAULT_GROUP = 'Salts'
    SCENARIO_ID_OPTION = 'test_ini_id'

    def __init__(self, root, exclude):
        self.dir_path = root
        self.exclude_names = exclude
        try:
            g = Group.objects.get(name=IniCtrl.DEFAULT_GROUP)
        except Group.DoesNotExist:
            g = Group(name=IniCtrl.DEFAULT_GROUP)
            g.save()
            log.info("Group '%s' has been added." % IniCtrl.DEFAULT_GROUP)
        self.default_group_id = g.id

    def _test_id_from_ini(self, scenario_path):
        config = ConfigParser()
        config.read(os.path.join(self.dir_path, scenario_path))
        try:
            return int(config.get(IniCtrl.SALTS_SECTION,
                                  IniCtrl.SCENARIO_ID_OPTION))
        except (NoOptionError, NoSectionError):
            return 0

    def _add_test_id(self, scenario_path, test_id):
        old_test_id = self._test_id_from_ini(scenario_path)
        if test_id == old_test_id:
            return

        section_line = "[%s]" % IniCtrl.SALTS_SECTION
        default_line = "[DEFAULT]"
        config = ConfigParser()
        ini_path = os.path.join(self.dir_path, scenario_path)
        config.read(ini_path)
        if IniCtrl.SALTS_SECTION not in config.sections():
            with open(ini_path, "a") as f:
                f.write("\n%s\n" % section_line)
        content = []
        with open(ini_path, "r") as f:
            content = f.readlines()
        ix = 0
        section_found = False
        for line in content:
            strip_line = line.strip()
            if section_found:
                if re.match("^ *\[.*\]", line):
                    section_found = False
                    continue
                pat = "^ *%s *=" % IniCtrl.SCENARIO_ID_OPTION
                if re.match(pat, strip_line):
                    del(content[ix])
                    content.insert(ix, "%s = %s\n" \
                                   % (IniCtrl.SCENARIO_ID_OPTION, test_id))
                    break
            if strip_line == section_line:
                section_found = True
                if not old_test_id:
                    content.insert(ix + 1,
                                   "%s = %s\n" \
                                   % (IniCtrl.SCENARIO_ID_OPTION, test_id))
                    break
            ix += 1
        with open(ini_path, "w") as f:
            f.writelines("".join(content))

    def _last_test_id(self):
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM salts_testini "
                       "ORDER BY id DESC LIMIT 1")
        res = cursor.fetchall()
        if not res:
            return 0
        return res[0][0]

    def set_scenario_status(self, scenario_path, status_value):
        try:
            t = Scenario.objects.get(scenario_path=scenario_path)
            t.status = status_value
            t.save()
            if status_value == 'D':
                del_path = os.path.join(self.dir_path, scenario_path)
                if os.path.exists(del_path):
                    os.remove(del_path)
            return True
        except Scenario.DoesNotExist:
            return False

    def get_root(self):
        return self.dir_path

    def get_scenario_pathes(self, status_value):
        res = Scenario.objects.filter(status=status_value)
        return [r.scenario_path for r in res]

    def get_test_id(self, scenario_path, from_db=False):
        if from_db:
            try:
                t = Scenario.objects.get(scenario_path=scenario_path)
                return t.id
            except Scenario.DoesNotExist:
                return 0
        else:
            if not self.dir_path:
                return 0
            return self._test_id_from_ini(scenario_path)

    def get_group_id(self, scenario_path):
        try:
            t = Scenario.objects.get(scenario_path=scenario_path)
            return t.group_id
        except Scenario.DoesNotExist:
            return 0

    def get_scenario_name(self, scenario_path):
        config = ConfigParser()
        ini_path = os.path.join(self.dir_path, scenario_path)
        test_name = ''
        if os.path.exists(ini_path):
            config.read(ini_path)
            try:
                test_name = config.get(IniCtrl.REPORT_SECTION, 'test_name')
            except (NoSectionError, NoOptionError):
                log.warning("Config %s is not scenario: "
                            "there is not 'test_name' option "
                            "in the 'sputnikreport' section." % ini_path)
        else:
            log.warning("Config %s is not found." % ini_path)
        return test_name

    def sync(self):
        scenario_pathes = ini_files(self.dir_path)
        absent_ini_pathes = []
        for spath in scenario_pathes:
            ini_test_id = self.get_test_id(spath, from_db=False)
            db_test_id = self.get_test_id(spath, from_db=True)
            if ini_test_id:
                if db_test_id:
                    if ini_test_id == db_test_id:
                        continue
                    else:
                        self._add_test_id(spath, db_test_id)
                else:
                    res = Scenario.objects.filter(id=ini_test_id)
                    if res:
                        if os.path.exists(os.path.join(self.dir_path,
                                                       res[0].scenario_path)):
                            raise IniDuplicateError("Two ini files %s and %s "
                                                    "have same test id." \
                                                    % (spath,
                                                       res[0].scenario_path))
                        else:
                            res[0].delete()
                    t = Scenario(id=ini_test_id,
                                scenario_path=spath,
                                group_id=self.default_group_id,
                                status='A')
                    t.save()
            else:
                if db_test_id:
                    self._add_test_id(spath, db_test_id)
                else:
                    absent_ini_pathes.append(spath)
        if absent_ini_pathes:
            with open("/tmp/1.csv", "w") as f:
                id = self._last_test_id() + 1
                for spath in absent_ini_pathes:
                    rec = []
                    rec.append(str(id))
                    rec.append(spath)
                    rec.append("A")
                    rec.append(str(self.default_group_id))
                    f.write(";".join(rec) + "\n")
                    self._add_test_id(spath, id)
                    id += 1
            with open("/tmp/1.csv", "r") as f:
                cursor = connection.cursor()
                cursor.copy_from(f, "salts_testini", sep=";")
        for spath in self.get_scenario_pathes("A"):
            if spath not in scenario_pathes:
                self.set_scenario_status(spath, "D")



ini_manager = IniCtrl(LT_PATH, EXCLUDE_INI_FILES)
