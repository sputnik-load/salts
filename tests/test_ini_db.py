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
    exclude_names = ["common.ini", "user.ini", "graphite*.ini"]

    def _check_table_content(self, ini_ctrl, scenario_pathes, del_pathes=[], expected=True):
        for spath in scenario_pathes:
            file_test_id = ini_ctrl.get_test_id(spath)
            db_test_id = ini_ctrl.get_test_id(spath, from_db=True)
            assert file_test_id == db_test_id
            assert ini_ctrl.get_group_id(spath) == 1
        db_del_pathes = ini_ctrl.get_scenario_pathes('D')
        for dp in db_del_pathes:
            assert not os.path.exists(os.path.join(ini_ctrl.get_root(), dp))
        for dpath in del_pathes:
            assert not (dpath in db_del_pathes) ^ expected

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
        base_dir = str(tmpdir.realpath())
        ini_ctrl = IniCtrl(base_dir, TestIniCtrl.exclude_names)

        ini_f = ["1.ini", "2.ini", "common1.ini"]
        no_ini_f = ["1.txt", "2.", "3"]
        specific_ini_f = ["common.ini", "graphite.ini", "graphite1.ini"]
        files = ini_f + no_ini_f + specific_ini_f
        dirs = ["", "sub1", "sub2"]
        self._create_files(tmpdir, files, dirs)

        ini_ctrl.sync()
        scenario_pathes = ini_ctrl.get_scenario_pathes('A')

        sub = []
        for d in dirs:
            if d:
                sub.append(d)
            check_files(scenario_pathes, base_dir, sub, ini_f, True)
            check_files(scenario_pathes, base_dir, sub, no_ini_f, False)
            check_files(scenario_pathes, base_dir, sub, specific_ini_f, False)
        assert ini_ctrl.get_root() == base_dir
        self._check_table_content(ini_ctrl, scenario_pathes)

    def test_content(self, tmpdir):
        base_dir = str(tmpdir.realpath())
        ini_ctrl = IniCtrl(base_dir, TestIniCtrl.exclude_names)
        files = [{"name": "scenario_wo_sect.ini", "content": "[test]"},
                 {"name": "scenario_with_sect.ini", "content": "[sputnikreport]\nt=1\n"}
                ]
        self._create_files(tmpdir, files)
        ini_ctrl.sync()
        scenario_pathes = ini_ctrl.get_scenario_pathes('A')
        check_files(scenario_pathes,
                    ini_ctrl.get_root(), [], files, True)
        self._check_table_content(ini_ctrl, scenario_pathes)

    def test_delete(self, tmpdir):
        base_dir = str(tmpdir.realpath())
        ini_ctrl = IniCtrl(base_dir, TestIniCtrl.exclude_names)
        files = ["1.ini"]
        self._create_files(tmpdir, files)
        ini_ctrl.sync()
        scenario_pathes = ini_ctrl.get_scenario_pathes('A')
        check_files(scenario_pathes,
                    ini_ctrl.get_root(), [], files, True)
        self._check_table_content(ini_ctrl, scenario_pathes)

        for fpath in files:
            ini_ctrl.set_scenario_status(fpath, 'D')
        ini_ctrl.sync()
        scenario_pathes = ini_ctrl.get_scenario_pathes('A')
        check_files(scenario_pathes,
                    ini_ctrl.get_root(), [], files, False)
        self._check_table_content(ini_ctrl, scenario_pathes, files, True)

    def test_move(self, tmpdir):
        dupl_name = "2.ini"
        base_dir = str(tmpdir.realpath())
        ini_ctrl = IniCtrl(base_dir, TestIniCtrl.exclude_names)

        files = [dupl_name]
        self._create_files(tmpdir, files)
        ini_ctrl.sync()
        scenario_pathes = ini_ctrl.get_scenario_pathes('A')
        check_files(scenario_pathes,
                    ini_ctrl.get_root(), [], files, True)
        self._check_table_content(ini_ctrl, scenario_pathes)

        dupl_test_id = ini_ctrl.get_test_id(dupl_name, from_db=True)
        srcfile = os.path.join(ini_ctrl.get_root(), dupl_name)
        dstdir = os.path.join(ini_ctrl.get_root(), "sub_a")
        os.makedirs(dstdir)
        shutil.copy(srcfile, dstdir)
        assert os.path.exists(os.path.join(dstdir, dupl_name))

        with pytest.raises(IniDuplicateError) as excinfo:
            ini_ctrl.sync()
        # print "e: %s" % excinfo
        os.unlink(srcfile)
        ini_ctrl.sync()
        assert ini_ctrl.get_test_id(dupl_name, from_db=True) == 0
        assert ini_ctrl.get_test_id("%s/%s" % ("sub_a", dupl_name), from_db=True) == dupl_test_id
