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
    for item in files:
        if type(item) is str:
            p = tmp.join(item)
            p.write("[sputnikreport]")
        if type(item) is dict:
            p = tmp.join(item["name"])
            p.write(item["content"])


def check_files(scenario_pathes, base_dir, sub, files, expected):
    sub_dir_path = "/".join(sub)
    dir_path = os.path.join(base_dir, sub_dir_path)
    for item in files:
        if type(item) is str:
            assert not (item in scenario_pathes) ^ expected
        if type(item) is dict:
            assert not (item["name"] in scenario_pathes) ^ expected


# pytestmark = pytest.mark.django_db

@pytest.mark.django_db
class TestIniCtrl(object):

    pytestmark = pytest.mark.django_db
    ini_ctrl = IniCtrl()
    tmp = None
    exclude_names = ["common.ini", "user.ini", "graphite*.ini"]

    def _check_table_content(self, scenario_pathes):
        for spath in scenario_pathes:
            print "\nspath: %s" % os.path.join(TestIniCtrl.ini_ctrl.get_root(),
                                             spath)
            file_test_id = TestIniCtrl.ini_ctrl.get_test_id(spath)
            db_test_id = TestIniCtrl.ini_ctrl.get_test_id(spath, from_db=True)
            assert file_test_id == db_test_id
            assert TestIniCtrl.ini_ctrl.get_group_id(spath) == 1

    def _insert_pathes(self, scenario_pathes):
        with open("/tmp/1.csv", "w") as f:
            id = 0
            sys.stdin = StringIO.StringIO()
            for spath in scenario_pathes:
                values = []
                id += 1
                values.append(str(id))
                fields = {}
                values.append(spath)
                values.append("1")
                values.append("A")
                f.write(";".join(values) + "\n")
        with open("/tmp/1.csv", "r") as f:
            cursor = connection.cursor()
            cursor.copy_from(f, "salts_testini", sep=";")
        self._check_table_content(scenario_pathes)
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
        scenario_pathes = TestIniCtrl.ini_ctrl.find_ini_files(base_dir, TestIniCtrl.exclude_names)
        sub = []
        for d in dirs:
            if d:
                sub.append(d)
            check_files(scenario_pathes, base_dir, sub, ini_f, True)
            check_files(scenario_pathes, base_dir, sub, no_ini_f, False)
            check_files(scenario_pathes, base_dir, sub, specific_ini_f, False)
        assert TestIniCtrl.ini_ctrl.get_root() == base_dir
        TestIniCtrl.tmp = tmpdir

    def test_sync(self):
        files = [{"name": "scenario_wo_sect.ini", "content": "[test]"},
                 {"name": "scenario_with_sect.ini", "content": "[sputnikreport]\nt=1\n"}
                ]
        self._create_files(TestIniCtrl.tmp, files)
        scenario_pathes = TestIniCtrl.ini_ctrl.find_ini_files(TestIniCtrl.ini_ctrl.get_root(),
                                                              TestIniCtrl.exclude_names)
        check_files(scenario_pathes,
                    TestIniCtrl.ini_ctrl.get_root(), [], files, True)
        TestIniCtrl.ini_ctrl.sync()
        self._check_table_content(scenario_pathes)
