import os
from glob import glob
from settings import LT_PATH, EXCLUDE_INI_FILES


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
