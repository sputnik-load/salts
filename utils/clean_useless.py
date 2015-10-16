#!/usr/bin/python

import psycopg2
import sys
import subprocess
import os
import logging
from optparse import OptionParser

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
    parser = OptionParser()
    parser.add_option("-p", "--tr-path", 
                        dest = "tr_path", 
                        help = "The path to the folder useless files should be removed from.")
    parser.add_option("-s", "--tr-subfolder", 
                        dest = "tr_subfolder",
                        help = "The subfolder name saved into DB.")
    parser.add_option("-l", "--log-filename", 
                        dest = "log_filename",
                        default = "",
                        help = "The path to the log file.")
    parser.add_option("-d", "--dry-run", 
                        dest = "dry_run", 
                        action = "store_true", default = False, 
                        help = "The script only shows files which are useless.")
    parser.add_option("-v", "--verbose", 
                        dest = "verbose", 
                        action = "store_true", default = False, 
                        help = "Verbose mode.")
    parser.add_option("-q", "--quiet", 
                        dest = "quiet", 
                        action = "store_true", default = False, 
                        help = "Quiet mode.")
    (options, args) = parser.parse_args()
    opts = dict()
    if not options.tr_path:
        raise Exception("Required <tr-path> option value is absent. Run with --help.")
    if not options.tr_subfolder:
        raise Exception("Required <tr-subfolder> option value is absent. Run with --help.")
    return options

class Logger():

    _logger = None

    def get_logger(self, log_filename, verbose, quiet):
        if self._logger == None: 
            self._logger = logging.getLogger("clean_useless")
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


class UselessTR():

    def __init__(self, options, logger):
        self._options = options
        self._logger = logger.get_logger(
                            self._options.log_filename, self._options.verbose,
                            self._options.quiet)
        self._media_res_path = self._options.tr_path
        self._subfolder = self._options.tr_subfolder
            
    def _get_db_ref(self, db_records): 
        db_ref = []
        for rec in db_records:
            db_ref += [item for item in rec if item]
        return db_ref
 
    def get_media_res_path(self):
        return self._media_res_path

    def saved_log_files(self):
        output = check_output(["find", "%s/%s/" % (self._media_res_path, self._subfolder), "-type", "f"])
        return output.replace("%s/" % self._media_res_path, "").split("\n")[:-1]

    def db_file_references(self):
        conn_string = "host='salt-dev.dev.ix.km' dbname='salts' user='salts' password='salts'"
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        query = """ select metrics, jm_jtl, phout, yt_log, jm_log, ph_conf, yt_conf,
                    modified_jmx, console_log, report_txt, jm_log_2 
                    from salts_testresult """
        cursor.execute(query)
        return self._get_db_ref(cursor.fetchall)
        
    def useless_files(self, log_files, db_ref):
        return ["%s/%s" % (self._media_res_path, lf) for lf in log_files if not lf in db_ref]

    def remove_empty_folders(self, path):
        if not os.path.isdir(path):
            return

        files = os.listdir(path)
        if len(files):
            for f in files:
                full_path = os.path.join(path, f)
                if os.path.isdir(full_path):
                    self.remove_empty_folders(full_path)

        files = os.listdir(path)
        if not len(files):
            if self._options.dry_run:
                msg = "Empty %s folder should be removed." % path
            else:
                os.rmdir(path)                
                msg = "Empty %s folder was removed." % path
            self._logger.info(msg)
 
    def remove_useless_files(self, ul_files):
        for ulf in ul_files:
            if self._options.dry_run:
                msg = "Useless %s file should be removed." % ulf
            else:
                os.remove(ulf)
                msg = "Useless %s file was removed." % ulf
            self._logger.info(msg)

    def dead_db_file_references(self, log_files, db_ref):
        return [rf for rf in db_ref if not rf in log_files]

    def log_dead_references(self, dead_ref):
        for drf in dead_ref:
            self._logger.info("Dead reference %s was found." % drf)
         
def main():
    try:
        options = parse_options()
        logger = Logger()
        u_tr = UselessTR(options, logger)
        log_files = u_tr.saved_log_files()
        db_ref = u_tr.db_file_references()
        ul_files = u_tr.useless_files(log_files, db_ref)
        u_tr.remove_useless_files(ul_files)
        u_tr.remove_empty_folders(u_tr.get_media_res_path())
        dead_ref = u_tr.dead_db_file_references(log_files, db_ref)        
    except Exception, e:
        print "Exception: %s" % e

if __name__ == "__main__":
	main()

