import os
from glob import glob
from settings import LT_PATH, EXCLUDE_INI_FILES
from salts.models import TestIni


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
                ini.append(full_path)
    return ini


class IniCtrl(object):

    def __init__(self):
        self.filepathes = []
        self.db_ini_files = []
        self.dir_path = ""

    def find_ini_files(self, dir_path, exclude_names):
        self.filepathes = ini_files(dir_path, exclude_names)
        self.dir_path = dir_path
        return self.filepathes

    def get_root(self):
        return self.dir_path

    def get_ini_files(self):
        return self.filepathes

    def select_db_ini_files(self):
        self.db_ini_files = TestIni.objects.all()

    def get_db_ini_files(self):
        if not self.db_ini_files:
            self.select_db_ini_files()
        return self.db_ini_files

    def sync(self):
        pass


