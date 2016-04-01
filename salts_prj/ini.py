import os
from settings import LT_PATH, EXCLUDE_INI_FILES


def ini_files(dir_path, exclude_names):
    ini = []
    for root, dirs, files in os.walk(dir_path, topdown=False):
        for name in files:
            full_path = os.path.join(root, name)
            file_name, file_ext = os.path.splitext(full_path)
            if file_ext == ".ini":
                ini.append(full_path)
    return ini
