import os
from salts_prj.ini import ini_files


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


def test_ini_files(tmpdir):
    ini_f = ["1.ini", "2.ini", "common1.ini"]
    no_ini_f = ["1.txt", "2.", "3"]
    specific_ini_f = ["common.ini", "graphite.ini", "graphite1.ini"]
    files = ini_f + no_ini_f + specific_ini_f
    dirs = ["", "sub1", "sub2"]
    sub = []
    for d in dirs:
        if d:
            sub.append(d)
        join_files(tmpdir, files, sub)
    base_dir = str(tmpdir.realpath())
    exclude_names = ["common.ini", "user.ini", "graphite*.ini"]
    found = ini_files(base_dir, exclude_names)
    sub = []
    for d in dirs:
        if d:
            sub.append(d)
        check_files(found, base_dir, sub, ini_f, True)
        check_files(found, base_dir, sub, no_ini_f, False)
        check_files(found, base_dir, sub, specific_ini_f, False)
