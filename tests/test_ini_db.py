# -*- coding: utf-8 -*-

import pytest
import os
import re
import sys
import StringIO
from django.db import connection
from django.db.utils import (DEFAULT_DB_ALIAS, ConnectionHandler)
from salts_prj.ini import ini_files, IniCtrl
from salts.models import TestIni, GroupIni


def join_files(tmpdir, files, sub):
    tmp = tmpdir
    if sub:
        for s in sub:
            if s:
                if os.path.exists(os.path.join(str(tmp.realpath()), s)):
                    tmp = tmp.join(s)
                else:
                    tmp = tmp.mkdir(s)
    for fname in files:
        p = tmp.join(fname)
        p.write("content")


def check_files(found, base_dir, sub, fnames, expected):
    sub_dir_path = "/".join(sub)
    dir_path = os.path.join(base_dir, sub_dir_path)
    for fn in fnames:
        file_path = os.path.join(dir_path, fn)
        assert not (file_path in found) ^ expected

# pytestmark = pytest.mark.django_db

@pytest.mark.django_db
class TestIniCtrl(object):

    pytestmark = pytest.mark.django_db
    ini_ctrl = IniCtrl()
    tmp = None
    exclude_names = ["common.ini", "user.ini", "graphite*.ini"]

    def _check_table_content(self, pathes):
        db_ini_files = TestIniCtrl.ini_ctrl.get_db_ini_files()
        for ini_file in db_ini_files:
            assert "%s/%s" % (TestIniCtrl.ini_ctrl.get_root(), ini_file.scenario_id) in pathes
        assert len(db_ini_files) == len(pathes)

    def _insert_pathes(self, pathes):
        with open("/tmp/1.csv", "w") as f:
            id = 0
            sys.stdin = StringIO.StringIO()
            for path in pathes:
                values = []
                id += 1
                values.append(str(id))
                fields = {}
                values.append(re.sub("%s/" % TestIniCtrl.ini_ctrl.get_root(),
                                     "", path))
                values.append("1")
                f.write(";".join(values) + "\n")
        with open("/tmp/1.csv", "r") as f:
            cursor = connection.cursor()
            cursor.copy_from(f, "salts_testini", sep=";")
        self._check_table_content(pathes)
        os.unlink("/tmp/1.csv")

    def _create_files(self, tmpdir, file_pathes, dir_names = [""]):
        sub = []
        for d in dir_names:
            if d:
                sub.append(d)
            join_files(tmpdir, file_pathes, sub)

    def setup_class(cls):
        cursor = connection.cursor()
        db_settings = cursor.db.settings_dict
        print "\nCurrent db_settings: %s" % db_settings
        g = GroupIni.objects.get(id=1)
        assert g.codename == "unknown"

    def test_find_ini_files(self, tmpdir):
        ini_f = ["1.ini", "2.ini", "common1.ini"]
        no_ini_f = ["1.txt", "2.", "3"]
        specific_ini_f = ["common.ini", "graphite.ini", "graphite1.ini"]
        files = ini_f + no_ini_f + specific_ini_f
        dirs = ["", "sub1", "sub2"]
        self._create_files(tmpdir, files, dirs)

        base_dir = str(tmpdir.realpath())
        found = TestIniCtrl.ini_ctrl.find_ini_files(base_dir, TestIniCtrl.exclude_names)
        sub = []
        for d in dirs:
            if d:
                sub.append(d)
            check_files(found, base_dir, sub, ini_f, True)
            check_files(found, base_dir, sub, no_ini_f, False)
            check_files(found, base_dir, sub, specific_ini_f, False)
        assert TestIniCtrl.ini_ctrl.get_root() == base_dir
        TestIniCtrl.tmp = tmpdir

    def test_load_db(self):
        ini_pathes = TestIniCtrl.ini_ctrl.get_ini_files()
        self._insert_pathes(ini_pathes)

    def test_sync(self):
        files = ["4.ini"]
        self._create_files(TestIniCtrl.tmp, files)
        found = TestIniCtrl.ini_ctrl.find_ini_files(TestIniCtrl.ini_ctrl.get_root(),
                                                    TestIniCtrl.exclude_names)
        check_files(found, TestIniCtrl.ini_ctrl.get_root(), [], files, True)
        TestIniCtrl.ini_ctrl.sync()
