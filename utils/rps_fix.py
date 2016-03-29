#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import argparse
import re
import logging
import psycopg2
import ConfigParser
from process_expired_const import CONFIG_ABSENT_EXC, \
    SECTION_ABSENT_EXC, OPTION_ABSENT_EXC, DB_SETTINGS_INI


def parse_args():
    parser = argparse.ArgumentParser(description="TESTING-2776.")
    parser.add_argument("-d", "--db-name",
                        dest="db_name")
    args = parser.parse_args()
    return args


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


class RPSFixer(object):

    def __init__(self, options, logger, db_settings_path=DB_SETTINGS_INI):
        self._db_settings = None
        self._conn = None
        self._db_settings_path = db_settings_path
        self._options = options
        self._log = logger.get_logger("rps_fix", "rps.log")
        self._read_db_config()
        self._log.info("RPS Fixer started ...")

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

    def connect_db(self):
        conn_string_templ = "host='%s' dbname='%s' user='%s' password='%s'"
        settings = (self._db_settings["host"], self._options.db_name,
                    self._db_settings["user"], self._db_settings["password"])
        self._conn = psycopg2.connect(conn_string_templ % settings)
        msg = "Connection with '%s' DB was created." % self._options.db_name
        self._log.info(msg)
        return self._conn

    def disconnect_db(self):
        if self._conn:
            self._conn.close()
            self._conn = None
            msg = "Connection with '%s' DB was closed." % self._options.db_name
            self._log.info(msg)

    def rps_from_schedule(self, rps_line):
        load_scheme = {"step": "step\(.*?(\d+),.*?(\d+),.*?\)",
                       "line": "line\(.*?(\d+),.*?(\d+),.*?\)",
                       "const": "const\(.*?(\d+),.*?\)"}
        rps_schedules = rps_line.split(";")
        rps = []
        for schedule in rps_schedules:
            values = []
            for load in load_scheme:
                matches = re.findall(load_scheme[load], schedule)
                if matches:
                    for m in matches:
                        values += list(m)
            if values:
                rps.append(max([int(v) for v in values]))
        rps_value = 0
        if rps:
            rps_value = sum(rps)
        return rps_value

    def convert_rps(self):
        self._log.info("Convert RPS")
        cursor = self._conn.cursor()
        sel_query = """ SELECT id, rps
                        FROM salts_testresult
                        WHERE rps like '%(%'
                    """
        upd_query_templ = "UPDATE salts_testresult SET rps={rps} WHERE id={id}"
        cursor.execute(sel_query)
        result = cursor.fetchall()
        for rec in result:
            (tr_id, schedule) = rec
            rps_value = self.rps_from_schedule(schedule)
            self._log.info("id: %s; rps_schedule: %s => rps: %s" % (tr_id, schedule, rps_value))
            upd_query = upd_query_templ.format(rps=rps_value, id=tr_id)
            cursor.execute(upd_query)
            self._conn.commit()
        cursor.close()

def main():
    args = parse_args()
    log = Logger()
    fix = RPSFixer(args, log)
    fix.connect_db()
    fix.convert_rps()
    fix.disconnect_db()


if __name__ == "__main__":
    main()
