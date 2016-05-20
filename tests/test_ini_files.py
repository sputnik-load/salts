import os
from salts_prj.ini import ini_files


def join_files(tmpdir, files, sub, test_name):
    tmp = tmpdir
    if sub:
        for s in sub:
            if s:
                if os.path.exists(os.path.join(str(tmp.realpath()), s)):
                    tmp = tmp.join(s)
                else:
                    tmp = tmp.mkdir(s)
    for fname in files:
        if test_name:
            p = tmp.join(fname)
            p.write("[sputnikreport]\ntest_name=%s\n" % test_name)
        else:
            p = tmp.join(fname)
            p.write("[sputnikreport]\n")


def check_files(found, base_dir, sub, fnames, expected):
    sub_dir_path = "/".join(sub)
    dir_path = os.path.join(base_dir, sub_dir_path)
    for fn in fnames:
        rel_path = os.path.join(sub_dir_path, fn)
        assert not (rel_path in found) ^ expected


def test_ini_files(tmpdir):
    scenarios = ['1.ini', '2.ini', 'common1.ini']
    not_scenarios = ['1.txt', '2.', '3', 'common.ini']
    dirs = ['', 'sub1', 'sub2']
    sub = []
    for d in dirs:
        if d:
            sub.append(d)
        join_files(tmpdir, scenarios, sub, test_name='a')
        join_files(tmpdir, not_scenarios, sub, test_name=None)
    base_dir = str(tmpdir.realpath())
    found = ini_files(base_dir)
    sub = []
    for d in dirs:
        if d:
            sub.append(d)
        check_files(found, base_dir, sub, scenarios, True)
        check_files(found, base_dir, sub, not_scenarios, False)
