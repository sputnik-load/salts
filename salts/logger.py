# -*- coding: utf-8 -*-

import sys
import logging


LOG_FILENAME_DEFAULT = "salts.log"
LOGGER_NAME = "salts"


class Logger(object):

    logger = None

    @staticmethod
    def get_logger(name=LOGGER_NAME,
                   log_filename=LOG_FILENAME_DEFAULT,
                   verbose=False,
                   quiet=False):
        if Logger.logger is None:
            Logger.logger = logging.getLogger(name)
            Logger.logger.setLevel(logging.DEBUG)
            templ_str = "%(asctime)s: [%(levelname)s]: %(message)s"
            verbose_templ_str = "%(asctime)s: [%(levelname)s]: [%(pathname)s:%(funcName)s:%(lineno)d]: %(message)s"

            if log_filename:
                fh = logging.FileHandler(log_filename)
                fh.setLevel(logging.DEBUG)
                if verbose:
                    fh.setFormatter(logging.Formatter(verbose_templ_str))
                else:
                    fh.setFormatter(logging.Formatter(templ_str))
                Logger.logger.addHandler(fh)

            console_handler = logging.StreamHandler(sys.stdout)
            stderr_handler = logging.StreamHandler(sys.stderr)

            fmt_verbose = logging.Formatter(verbose_templ_str)
            fmt_regular = logging.Formatter(templ_str, "%H:%M:%S")

            if verbose:
                console_handler.setLevel(logging.DEBUG)
                stderr_handler.setLevel(logging.ERROR)
                console_handler.setFormatter(fmt_verbose)
                stderr_handler.setFormatter(fmt_verbose)
            elif quiet:
                console_handler.setLevel(logging.WARNING)
                stderr_handler.setLevel(logging.ERROR)
                console_handler.setFormatter(fmt_regular)
                stderr_handler.setFormatter(fmt_regular)
            else:
                console_handler.setLevel(logging.INFO)
                stderr_handler.setLevel(logging.ERROR)
                console_handler.setFormatter(fmt_regular)
                stderr_handler.setFormatter(fmt_regular)

            Logger.logger.addHandler(console_handler)
            # Logger.logger.addHandler(stderr_handler)
        return Logger.logger
