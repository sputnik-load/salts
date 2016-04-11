# -*- coding: utf-8 -*-

import pytest
import os
import re
import sys
import shutil
import StringIO
from django.db import connection
from django.db.utils import (DEFAULT_DB_ALIAS, ConnectionHandler)
from salts_prj.ini import ini_files, IniCtrl, IniDuplicateError
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


@pytest.mark.django_db
class TestIniCtrl(object):

    pytestmark = pytest.mark.django_db
    ini_ctrl = IniCtrl()
    tmp = None
    exclude_names = ["common.ini", "user.ini", "graphite*.ini"]

    def _check_table_content(self, scenario_pathes, del_pathes=[], expected=True):
        for spath in scenario_pathes:
            file_test_id = TestIniCtrl.ini_ctrl.get_test_id(spath)
            db_test_id = TestIniCtrl.ini_ctrl.get_test_id(spath, from_db=True)
            assert file_test_id == db_test_id
            assert TestIniCtrl.ini_ctrl.get_group_id(spath) == 1
        db_del_pathes = TestIniCtrl.ini_ctrl.deleted_scenario_pathes()
        for dp in db_del_pathes:
            assert not os.path.exists(os.path.join(TestIniCtrl.ini_ctrl.get_root(), dp))
        for dpath in del_pathes:
            assert not (dpath in db_del_pathes) ^ expected


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
        # print "\nCurrent db_settings: %s" % db_settings
        g = GroupIni.objects.get(id=1)
        assert g.codename == "unknown"

    def test_sync(self, tmpdir):

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

        scenario_pathes = TestIniCtrl.ini_ctrl.find_ini_files(TestIniCtrl.ini_ctrl.get_root(),
                                                              TestIniCtrl.exclude_names)
        TestIniCtrl.ini_ctrl.sync()
        self._check_table_content(scenario_pathes)

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

        files = ["1.ini"]
        for fpath in files:
            TestIniCtrl.ini_ctrl.set_scenario_status(fpath, 'D')
        scenario_pathes = TestIniCtrl.ini_ctrl.find_ini_files(TestIniCtrl.ini_ctrl.get_root(),
                                                              TestIniCtrl.exclude_names)
        check_files(scenario_pathes,
                    TestIniCtrl.ini_ctrl.get_root(), [], files, False)
        TestIniCtrl.ini_ctrl.sync()
        self._check_table_content(scenario_pathes, files, True)

        dupl_name = "2.ini"
        dupl_test_id = TestIniCtrl.ini_ctrl.get_test_id(dupl_name, from_db=True)
        srcfile = os.path.join(TestIniCtrl.ini_ctrl.get_root(), dupl_name)
        dstdir = os.path.join(TestIniCtrl.ini_ctrl.get_root(), "sub_a")
        os.makedirs(dstdir)
        shutil.copy(srcfile, dstdir)
        assert os.path.exists(os.path.join(dstdir, dupl_name))

        scenario_pathes = TestIniCtrl.ini_ctrl.find_ini_files(TestIniCtrl.ini_ctrl.get_root(),
                                                              TestIniCtrl.exclude_names)
        with pytest.raises(IniDuplicateError) as excinfo:
            TestIniCtrl.ini_ctrl.sync()
        # print "e: %s" % excinfo
        os.unlink(srcfile)
        scenario_pathes = TestIniCtrl.ini_ctrl.find_ini_files(TestIniCtrl.ini_ctrl.get_root(),
                                                              TestIniCtrl.exclude_names)
        TestIniCtrl.ini_ctrl.sync()
        assert TestIniCtrl.ini_ctrl.get_test_id(dupl_name, from_db=True) == 0
        assert TestIniCtrl.ini_ctrl.get_test_id("%s/%s" % ("sub_a", dupl_name), from_db=True) == dupl_test_id
