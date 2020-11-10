#! /bin/bash/python3.8
# -*- coding:utf8 -*

import logging
import logging.config
import os

from lib import loader
from config import constant


class Log(object):
    logger = None

    def getLog(self):
        return self.logger


@loader.config.register(look='logging', level=1)
def set_up(cfg):
    log_path = os.path.join(constant.CONF_PATH, cfg['config_file'])
    logging.config.fileConfig(log_path)
    Log.logger = logging.getLogger(cfg['default_logger'])
