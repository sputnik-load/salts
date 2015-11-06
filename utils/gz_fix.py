# -*- coding: utf-8 -*-

import sys
import os
import logging
import gzip
from optparse import OptionParser
from os.path import join


def parse_options():
    parser = OptionParser(description="TESTING-2326.")
    parser.add_option("-p", "--tr_path",
                      dest="tr_path")
    options = parser.parse_args()[0]
    return options


class Logger(object):

    _logger = None

    def get_logger(self, name, log_filename):
        if self._logger is None:
            self._logger = logging.getLogger(name)
            self._logger.setLevel(logging.DEBUG)
            templ_str = "%(asctime)s: [%(levelname)s]: %(message)s"

            if log_filename:
                fh = logging.FileHandler(log_filename)
                fh.setLevel(logging.DEBUG)
                fh.setFormatter(logging.Formatter(templ_str))
                self._logger.addHandler(fh)

            console_handler = logging.StreamHandler(sys.stdout)
            stderr_handler = logging.StreamHandler(sys.stderr)

            console_handler.setLevel(logging.INFO)
            stderr_handler.setLevel(logging.ERROR)

            self._logger.addHandler(console_handler)
            self._logger.addHandler(stderr_handler)
        return self._logger


class GZFixer(object):
    def __init__(self, options, logger):
        self._options = options
        self._options.tr_path = os.path.abspath(self._options.tr_path)
        self._logger = logger.get_logger("gz_fix", "gz.log")
        self._logger.info("Fixer init ...")

    def archives(self):
        arch = []
        for root, dirs, files in os.walk(self._options.tr_path, topdown=False):
            for name in files:
                full_path = join(root, name)
                file_name, file_ext = os.path.splitext(full_path)
                if file_ext == ".gz":
                    self._logger.info("%s archive found." % full_path)
                    arch.append(full_path)
        return arch

    def extract(self, archives):
        extracted_files = []
        for file_path in archives:
            while True:
                file_name, file_ext = os.path.splitext(file_path)
                if not file_ext == ".gz":
                    extracted_files.append(file_path)
                    break
                af = gzip.open(file_path, "rb")
                df = open(file_name, "wb")
                df.write(af.read())
                af.close()
                df.close()
                self._logger.info("%s extracted into %s" % (file_path,
                                                            file_name))
                os.remove(file_path)
                self._logger.info("%s archive file was removed." % file_path)
                file_path = file_name
        return extracted_files

    def archive_files(self, file_pathes):
        for file_path in file_pathes:
            arch_path = "%s.gz" % file_path
            cur_work_dir = os.getcwd()
            file_dir = os.path.dirname(file_path)
            file_name = os.path.basename(file_path)
            os.chdir(file_dir)
            with open(file_name, "rb") as lf:
                arch_file_name = "%s.gz" % (file_name)
                af = gzip.open(arch_file_name, "wb")
                af.writelines(lf.readlines())
                af.close()
            msg = "%s file was archived . "
            msg += "Archive path is %s."
            self._logger.info(msg % (file_path, arch_path))
            os.remove(file_path)
            self._logger.info("%s file was removed." % file_path)
            os.chdir(cur_work_dir)


def main():
    options = parse_options()
    logger = Logger()
    gz = GZFixer(options, logger)
    archives = gz.archives()
    extracted_files = gz.extract(archives)
    gz.archive_files(extracted_files)


if __name__ == "__main__":
    main()
