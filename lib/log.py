#! /bin/bash/python3.8
# -*- coding:utf8 -*

import logging
import logging.config
import os

from lib import configer
from lib import path

class Log(object):
    logger = None

    def getLog(self):
        return Log.logger

@configer.instance.register(look='logging', level=1)
def set_up(cfg) :
    log_path = os.path.join(path._CONF_PATH, cfg['config_file'])
    logging.config.fileConfig(log_path)
    Log.logger = logging.getLogger(cfg['default_logger'])

