import os
import re
import codecs
from glob import glob
from settings import LT_PATH, EXCLUDE_INI_FILES
from django.db import connection
from salts.models import TestIni
from ConfigParser import ConfigParser, NoSectionError, NoOptionError


def ini_files(dir_path, exclude_names):
    ini = []
    specific_names = {}
    specific_names[dir_path] = []
    for spec_name in exclude_names:
        specific_names[dir_path] += glob(os.path.join(dir_path, spec_name))
    for root, dirs, files in os.walk(dir_path, topdown=False):
        for name in dirs:
            full = os.path.join(root, name)
            specific_names[full] = []
            for spec_name in exclude_names:
                specific_names[full] += glob(os.path.join(full, spec_name))
    for root, dirs, files in os.walk(dir_path, topdown=False):
        for name in files:
            full_path = os.path.join(root, name)
            file_name, file_ext = os.path.splitext(full_path)
            if file_ext == ".ini" and (not full_path in specific_names[root]):
                ini.append(re.sub("%s/" % dir_path, "", full_path))
    return ini


class IniDuplicateError(Exception):
    pass

class IniCtrl(object):

    SECTION = "sputnikreport"

    def __init__(self, root, exclude):
        self.dir_path = root
        self.exclude_names = exclude

    def _test_id_from_ini(self, ini_path):
        config = ConfigParser()
        config.read(ini_path)
        try:
            return int(config.get(IniCtrl.SECTION, "test_id"))
        except (NoOptionError, NoSectionError):
            return 0

    def _add_test_id(self, ini_path, test_id):
        section_line = "[%s]" % IniCtrl.SECTION
        config = ConfigParser()
        config.read(ini_path)
        if IniCtrl.SECTION not in config.sections():
            with open(ini_path, "a") as f:
                f.write("\n%s\n" % section_line)
        content = []
        with open(ini_path, "r") as f:
            content = f.readlines()
        ix = 0
        for line in content:
            if line.strip() == section_line:
                content.insert(ix + 1, "test_id = %s" % test_id)
                break
            ix += 1
        with open(ini_path, "w") as f:
            f.writelines("\n".join(content))

    def _last_test_id(self):
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM salts_testini ORDER BY id DESC LIMIT 1")
        res = cursor.fetchall()
        if not res:
            return 0
        return res[0][0]

    def set_scenario_status(self, scen_id, status_value):
        try:
            t = TestIni.objects.get(scenario_id=scen_id)
            t.status = status_value
            t.save()
            if status_value == 'D':
                del_path = os.path.join(self.dir_path, scen_id)
                if os.path.exists(del_path):
                    os.remove(del_path)
            return True
        except TestIni.DoesNotExist:
            return False

    def get_root(self):
        return self.dir_path

    def get_scenario_pathes(self, status_value):
        res = TestIni.objects.filter(status=status_value)
        return [r.scenario_id for r in res]

    def get_test_id(self, scen_id, from_db=False):
        if from_db:
            try:
                t = TestIni.objects.get(scenario_id=scen_id)
                return t.id
            except TestIni.DoesNotExist:
                return 0
        else:
            if not self.dir_path:
                return 0
            return self._test_id_from_ini(os.path.join(self.dir_path, scen_id))

    def get_group_id(self, scen_id):
        try:
            t = TestIni.objects.get(scenario_id=scen_id)
            return t.group_ini_id
        except TestIni.DoesNotExist:
            return 0

    def sync(self):
        scenario_pathes = ini_files(self.dir_path, self.exclude_names)
        absent_ini_pathes = []
        for spath in scenario_pathes:
            test_id = self._test_id_from_ini(os.path.join(self.dir_path, spath))
            if test_id:
                if not self.get_test_id(spath, from_db=True):
                    t = TestIni.objects.get(id=test_id)
                    if os.path.exists(os.path.join(self.dir_path, t.scenario_id)):
                        raise IniDuplicateError("Two ini files %s and %s have same test id." % (spath, t.scenario_id))
                    t.scenario_id = spath
                    t.save()
            else:
                absent_ini_pathes.append(spath)
        if absent_ini_pathes:
            with open("/tmp/1.csv", "w") as f:
                id = self._last_test_id() + 1
                for spath in absent_ini_pathes:
                    rec = []
                    rec.append(str(id))
                    rec.append(spath)
                    rec.append("1")
                    rec.append("A")
                    f.write(";".join(rec) + "\n")
                    self._add_test_id(os.path.join(self.dir_path, spath), id)
                    id += 1
            with open("/tmp/1.csv", "r") as f:
                cursor = connection.cursor()
                cursor.copy_from(f, "salts_testini", sep=";")
        for spath in self.get_scenario_pathes("A"):
            if spath not in scenario_pathes:
                self.set_scenario_status(spath, "D")
