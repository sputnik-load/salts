# -*- coding: utf-8 -*-

import sys
import os
import re
import logging
import gzip
import psycopg2
import ConfigParser
from optparse import OptionParser
from os.path import join
from process_expired_const import CONFIG_ABSENT_EXC, \
    SECTION_ABSENT_EXC, OPTION_ABSENT_EXC, DB_SETTINGS_INI


def parse_options():
    parser = OptionParser(description="TESTING-2326.")
    parser.add_option("-p", "--tr_path",
                      dest="tr_path")
    parser.add_option("-d", "--db-name",
                      dest="db_name")
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


class DBConfigError(Exception):
    pass


class GZFixer(object):
    def __init__(self, options, logger, db_settings_path=DB_SETTINGS_INI):
        self._db_settings = None
        self._conn = None
        self._artifacts = ["metrics", "jm_jtl", "phout",
                           "yt_log", "jm_log", "ph_conf",
                           "yt_conf", "modified_jmx",
                           "console_log", "report_txt",
                           "jm_log_2"]
        self._db_settings_path = db_settings_path
        self._options = options
        self._options.tr_path = os.path.expanduser(self._options.tr_path)
        self._options.tr_path = os.path.abspath(self._options.tr_path)
        self._logger = logger.get_logger("gz_fix", "gz.log")
        self._read_db_config()
        self._logger.info("Fixer init ...")

    def _read_db_config(self):
        if not os.path.exists(self._db_settings_path):
            raise DBConfigError(CONFIG_ABSENT_EXC % self._db_settings_path)
        db_config = ConfigParser.RawConfigParser()
        db_config.read(self._db_settings_path)
        sections = db_config.sections()
        if self._options.db_name not in sections:
            msg = SECTION_ABSENT_EXC % (self._options.db_name,
                                        self._db_settings_path)
            raise DBConfigError(msg)
        self._db_settings = {"host": "", "user": "", "password": ""}
        for k in self._db_settings:
            if not db_config.has_option(self._options.db_name, k):
                msg = OPTION_ABSENT_EXC % (k, self._options.db_name,
                                           self._db_settings_path)
                raise DBConfigError(msg)
            self._db_settings[k] = db_config.get(self._options.db_name, k)

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

    def connect_db(self):
        conn_string_templ = "host='%s' dbname='%s' user='%s' password='%s'"
        settings = (self._db_settings["host"], self._options.db_name,
                    self._db_settings["user"], self._db_settings["password"])
        self._conn = psycopg2.connect(conn_string_templ % settings)
        msg = "Connection with '%s' DB was created." % self._options.db_name
        self._logger.info(msg)
        return self._conn

    def modify_db(self, archives):
        cursor = self._conn.cursor()

        def upd_query(a, fp, ext):
            return "UPDATE salts_testresult \
SET {artif} = {artif} || '{arch_ext}' \
WHERE {artif} like '{file_path}%' \
AND NOT {artif} like '%.gz'".format(artif=a, file_path=fp, arch_ext=ext)
        for arch_path in archives:
            ext = ".gz"
            self._logger.info("Arch Path: %s" % arch_path)
            path = re.sub("^%s/" % self._options.tr_path, "", arch_path)
            path = re.sub(".gz", "", path)
            for a in self._artifacts:
                query = upd_query(a, path, ext * arch_path.count(ext))
                self._logger.info("Query: %s" % query)
                cursor.execute(query)
                self._conn.commit()
        cursor.close()

    def fix_db(self):
        cursor = self._conn.cursor()

        def upd_query(a):
            return "UPDATE salts_testresult \
SET {artif} = SUBSTRING({artif}, 0, POSITION('.gz' in {artif})) || '.gz' \
WHERE {artif} like '%.gz'".format(artif=a)
        for a in self._artifacts:
            query = upd_query(a)
            self._logger.info("Query: %s" % query)
            cursor.execute(query)
            self._conn.commit()
        cursor.close()

    def check_db(self, artif_files):
        cursor = self._conn.cursor()
        absent_files = []

        def sel_query(a, fp):
            return "SELECT id FROM salts_testresult \
WHERE {artif} = '{file_path}'".format(artif=a, file_path=fp)
        for artif in artif_files:
            self._logger.info("Artif Path: %s" % artif)
            path = re.sub("^%s/" % self._options.tr_path, "", artif)
            query = "\nUNION\n".join([sel_query(a, path)
                                      for a in self._artifacts])
            self._logger.info("Query: %s" % query)
            cursor.execute(query)
            result = cursor.fetchall()
            if not result:
                absent_files.append(artif)
            self._logger.info("Result: %s" % result)
        cursor.close()
        if not absent_files:
            self._logger.info("No absent files.")
            return True
        self._logger.info("Following files absent in DB: %s" % absent_files)
        return False

    def match_archive_records(self, archives):
        cursor = self._conn.cursor()

        def sel_query(a):
            return "SELECT id, {artif} as artifact FROM salts_testresult \
WHERE {artif} like '%.gz'".format(artif=a)
        query = "\nUNION\n".join([sel_query(a)
                                  for a in self._artifacts])
        cursor.execute(query)
        arch_files = []
        result = cursor.fetchall()
        if result:
            arch_files = [rec[1] for rec in result]
        cursor.close()

        archive_names = [re.sub("^%s/" % self._options.tr_path, "", path)
                         for path in archives]
        if set(archive_names) == set(arch_files):
            self._logger.info("OK: files and records in DB matched.")
        else:
            self._logger.info("FAILED: files and records in DB isn't matched.")
            self._logger.info("Arch Files: %s" % arch_files)
            self._logger.info("Archives: %s" % archive_names)
        return arch_files

    def disconnect_db(self):
        if self._conn:
            self._conn.close()
            self._conn = None
            msg = "Connection with '%s' DB was closed." % self._options.db_name
            self._logger.info(msg)


def main():
    options = parse_options()
    logger = Logger()
    gz = GZFixer(options, logger)
    gz.connect_db()
    archives = gz.archives()
    extracted_files = gz.extract(archives)
    gz.archive_files(extracted_files)
    gz.fix_db()
    archives = gz.archives()
    gz.match_archive_records(archives)
    gz.disconnect_db()


if __name__ == "__main__":
    main()
