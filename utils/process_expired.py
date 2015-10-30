# -*- coding: utf-8 -*-

import os
import datetime
import logging
import ConfigParser
import subprocess
from optparse import OptionParser
from process_expired_const import *

def check_output(*popenargs, **kwargs):
    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        error = subprocess.CalledProcessError(retcode, cmd)
        raise error
    return output    

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
    parser.add_option("-d", "--dry-run", 
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

class ExpiredHandler():
    def __init__(self, options, logger, 
                    time_config_path = TIME_CONFIG_INI,
                    db_settings_path = DB_SETTINGS_INI):
        self._options = options
        self._logger = logger.get_logger(
                        LOGGER_NAME,
                        self._options.log_filename, self._options.verbose,
                        self._options.quiet)
        self._time_config_name = time_config_path 
        self._db_settings_path = db_settings_path
        self._read_time_config()
        self._read_db_config()
        self._connect_db()
        self._logger.info("Expired handler init...")
 
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
                    raise TimeConfigError(OPTION_ABSENT_EXC %(tt, k, self._time_config_name))
            self._time_periods[k][tt] = time_config.get(k, tt)

    def _read_db_config(self):
        if not os.path.exists(self._db_settings_path):
            raise DBConfigError(CONFIG_ABSENT_EXC % self._db_settings_path)
        db_config = ConfigParser.RawConfigParser()
        db_config.read(self._db_settings_path)
        sections = db_config.sections()
        if not self._options.db_name in sections:
            raise DBConfigError(SECTION_ABSENT_EXC % (self._options.db_name, self._db_settings_path))
        self._db_settings = {"db_type": "", "host": "", "db_name": "", "user": ""}
        
    def _connect_db(self):
        pass

    def _get_log_files(self): 
        output = check_output(["find", "%s" % self._options.tr_path, "-type", "f"])
        return output.replace("%s/" % self._options.tr_path, "").split("\n")[:-1]

    def _get_log_file_date(self, file_name):
        return ""            
            
    def archive(self):
        log_files = self._get_log_files()
        for lf in log_files:
           dt = self._get_log_file_date(lf)

    def remove(self):
        pass
         

def main():
    try:
        options = parse_options()
        logger = Logger()
        eh = ExpiredHandler(options, logger)
        eh.archive()
        eh.remove()
    except Exception, e:
        print "Exception: %s" % e

if __name__ == "__main__":
	main()
#if not args.path:
#    print 

# gzip -c tank.log > tank.log.gzip - archive
# gzip -d tank.log - decompress


