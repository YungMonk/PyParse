#! /bin/bash/python3.8
# -*- coding:utf8 -*

import os
import sys


ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONF_PATH = os.path.join(ROOT_PATH, 'config')
LIB_PATH = os.path.join(ROOT_PATH, 'lib')
UTIL_PATH = os.path.join(ROOT_PATH, 'utils')
CONTROLLER_PATH = os.path.join(ROOT_PATH, 'controller')
TEMPLATE = os.path.join(ROOT_PATH, 'template/')
SCRIPT = os.path.join(ROOT_PATH, 'script/')
SCRIPT_FONT = os.path.join(SCRIPT, 'font/')

_path = ()
_path += CONF_PATH, LIB_PATH, UTIL_PATH, CONTROLLER_PATH, TEMPLATE, SCRIPT
map(sys.path.append, _path)
