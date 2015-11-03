# -*- coding: utf-8 -*-

import os
import logging
import ConfigParser
import psycopg2
import gzip
from optparse import OptionParser
from process_expired_const import *

def parse_options():
    parser = OptionParser(description = SCRIPT_DESC)
    parser.add_option("-p", "--tr-path",
                        dest = "tr_path",
                        help = TR_PATH_HELP)
    parser.add_option("-d", "--db-name",
                        dest = "db_name",
                        help = DB_NAME_HELP)
    parser.add_option("-l", "--log-filename",
                        dest = "log_filename",
                        default = LOG_FILENAME_DEFAULT,
                        help = LOG_FILENAME_HELP)
    parser.add_option("-r", "--dry-run",
                        dest = "dry_run",
                        action = "store_true", default = False,
                        help = DRY_RUN_HELP)
    parser.add_option("-v", "--verbose",
                        dest = "verbose",
                        action = "store_true", default = False,
                        help = VERBOSE_HELP)
    parser.add_option("-q", "--quiet",
                        dest = "quiet",
                        action = "store_true", default = False,
                        help = QUIET_HELP)
    (options, args) = parser.parse_args()
    if not options.tr_path:
        raise Exception(TR_PATH_ABSENT_EXC)
    return options

class Logger():

    _logger = None

    def get_logger(self, name, log_filename, verbose, quiet):
        if self._logger == None:
            self._logger = logging.getLogger(name)
            self._logger.setLevel(logging.DEBUG)

            if log_filename:
                fh = logging.FileHandler(log_filename)
                fh.setLevel(logging.DEBUG)
                fh.setFormatter(
                    logging.Formatter("%(asctime)s: [%(levelname)s]: %(message)s"))
                self._logger.addHandler(fh)

            console_handler = logging.StreamHandler(sys.stdout)
            stderr_handler = logging.StreamHandler(sys.stderr)

            fmt_verbose = logging.Formatter("%(asctime)s: [%(levelname)s]: %(message)s")
            fmt_regular = logging.Formatter("%(asctime)s: %(levelname)s: %(message)s", "%H:%M:%S")

            if verbose:
                console_handler.setLevel(logging.DEBUG)
                console_handler.setFormatter(fmt_verbose)
                stderr_handler.setFormatter(fmt_verbose)
            elif quiet:
                console_handler.setLevel(logging.WARNING)
                console_handler.setFormatter(fmt_regular)
                stderr_handler.setFormatter(fmt_regular)
            else:
                console_handler.setLevel(logging.INFO)
                stderr_handler.setLevel(logging.ERROR)
                console_handler.setFormatter(fmt_regular)
                stderr_handler.setFormatter(fmt_regular)

            self._logger.addHandler(console_handler)
            self._logger.addHandler(stderr_handler)
        return self._logger


class TimeConfigError(Exception): pass
class DBConfigError(Exception): pass

class ExpiredHandler(object):
    def __init__(self, options, logger,
                    time_config_path = TIME_CONFIG_INI,
                    db_settings_path = DB_SETTINGS_INI):
        self._conn = None
        self._options = options
        self._options.tr_path = os.path.abspath(self._options.tr_path)
        self._logger = logger.get_logger(
                        LOGGER_NAME,
                        self._options.log_filename, self._options.verbose,
                        self._options.quiet)
        self._time_config_name = time_config_path
        self._db_settings_path = db_settings_path
        self._read_time_config()
        self._read_db_config()
        self._logger.info("Expired handler init...")

    def __enter__(self):
        self.connect_db()

    def __exit__(self, a, b, c):
        self.disconnect_db()

    def _read_time_config(self):
        if not os.path.exists(self._time_config_name):
            raise TimeConfigError(CONFIG_ABSENT_EXC % self._time_config_name)
        time_config = ConfigParser.RawConfigParser()
        time_config.read(self._time_config_name)
        time_types = ["archive", "remove"]
        self._time_periods = {"metrics": {}, "jm_jtl": {}, "phout": {}, "yt_log": {}, 
                                "jm_log": {}, "ph_conf": {}, "yt_conf": {},
                                "modified_jmx": {}, "console_log": {},
                                "report_txt": {}, "jm_log_2": {}}
        for k in self._time_periods:
            if not time_config.has_section(k):
                raise TimeConfigError(SECTION_ABSENT_EXC % (k, self._time_config_name))
            for tt in time_types:
                if not time_config.has_option(k, tt):
                    raise TimeConfigError(OPTION_ABSENT_EXC % (tt, k, self._time_config_name))
                self._time_periods[k][tt] = time_config.get(k, tt)

    def _read_db_config(self):
        if not os.path.exists(self._db_settings_path):
            raise DBConfigError(CONFIG_ABSENT_EXC % self._db_settings_path)
        db_config = ConfigParser.RawConfigParser()
        db_config.read(self._db_settings_path)
        sections = db_config.sections()
        if not self._options.db_name in sections: 
            raise DBConfigError(SECTION_ABSENT_EXC % (self._options.db_name, self._db_settings_path))
        self._db_settings = {"host": "", "user": "", "password": ""}
        for k in self._db_settings:
            if not db_config.has_option(self._options.db_name, k):
                raise DBConfigError(
                        OPTION_ABSENT_EXC % (k, self._options.db_name,
                                                self._db_settings_path))
            self._db_settings[k] = db_config.get(self._options.db_name, k)

    def connect_db(self):
        conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % (
                        self._db_settings["host"],
                        self._options.db_name,
                        self._db_settings["user"],
                        self._db_settings["password"])
        self._conn = psycopg2.connect(conn_string)
        msg = "Connection with '%s' DB was created." % self._options.db_name
        self._logger.info(msg)
        return self._conn

    def disconnect_db(self):
        if self._conn:
            self._conn.close()
            self._conn = None
            msg = "Connection with '%s' DB was closed." % self._options.db_name
            self._logger.info(msg)

    def _get_affected_files(self, action):
        cursor = self._conn.cursor()
        query = ""
        has_union = True
        for log_type in self._time_periods:
            if not self._time_periods[log_type][action] == "-1":
                if not has_union: 
                    query += "\nUNION\n"
                    has_union = True
                query += """SELECT id, '%s', %s as log_type 
                            FROM salts_testresult 
                            WHERE date_trunc('day', dt_finish) < current_date - %s and %s <> ''
                        """ % (log_type, log_type, self._time_periods[log_type][action], log_type)
                has_union = False
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result

    def _archive_file(self, rec_id, log_type, log_path):
        msg = "%s log file should be archived (id=%s; log_type=%s)."
        self._logger.info(msg % (log_path, rec_id, log_type))
        if self._options.dry_run:
            return
        with open("%s/%s" % (self._options.tr_path, log_path), "rb") as log_file:
            arch_file = gzip.open("%s/%s.gz" % (self._options.tr_path, log_path), 
                                    "wb")
            arch_file.writelines(log_file.readlines())
            arch_file.close()
        msg = "%s log file was archived (id=%s; log_type=%s). " 
        msg += "Archive path is %s.gz." 
        self._logger.info(msg % (log_path, rec_id, log_type, log_path))

    def _update_record(self, rec_id, log_type, log_path, action = "clear"):
        new_log_path = ""
        if action == "archive":
            new_log_path = "%s.gz" % log_path
        msg = "Log path %s should be replaced with %s (id=%s; log_type=%s)."
        self._logger.info(msg % (log_path, new_log_path, rec_id, log_type))
        if self._options.dry_run:
            return
        cursor = self._conn.cursor()
        query = "UPDATE salts_testresult SET %s = '%s' WHERE id = %s" 
        cursor.execute(query % (log_type, new_log_path, rec_id))
        self._conn.commit()
        cursor.close()
        msg = "Log path %s was replaced with %s (id=%s; log_type=%s)."
        self._logger.info(msg % (log_path, new_log_path, rec_id, log_type))

    def _remove_log_file(self, log_path): 
        self._logger.info("Log file %s should be removed." % log_path)
        if self._options.dry_run:
            return
        os.remove("%s/%s" % (self._options.tr_path, log_path))
        self._logger.info("Log file %s was removed." % log_path)

    def archive(self):
        db_affected_recs = self._get_affected_files("archive")
        for record in db_affected_recs:
            (rec_id, log_type, log_path) = record
            if not os.path.exists("%s/%s" % (self._options.tr_path, log_path)):
                msg = "There is log path %s in DB (id=%s; log_type=%s), "
                msg += "but log file %s isn't exist."
                self._logger.warning(msg % (log_path, rec_id, log_type, 
                                            log_path))            
            else:
                self._archive_file(rec_id, log_type, log_path)
                self._update_record(rec_id, log_type, log_path, "archive")
                self._remove_log_file(log_path)

    def remove(self): 
        db_affected_recs = self._get_affected_files("remove")
        for record in db_affected_recs:
            (rec_id, log_type, log_path) = record
            if not os.path.exists("%s/%s" % (self._options.tr_path, log_path)):
                msg = "There is log path %s in DB (id=%s; log_type=%s), "
                msg += "but log file %s isn't exist."
                self._logger.warning(msg % (log_path, rec_id, log_type, 
                                            log_path))            
            else:
                self._update_record(rec_id, log_type, log_path)
                self._remove_log_file(log_path)

def main():
    try:
        options = parse_options()
        logger = Logger()
        eh = ExpiredHandler(options, logger)
        eh.connect_db()
        eh.remove()
        eh.archive()
        eh.disconnect_db()
    except Exception, e:
        print "Exception: %s" % e

if __name__ == "__main__":
	main()

