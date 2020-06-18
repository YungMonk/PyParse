#! /bin/bash/python3.8
# -*- coding:utf8 -*

import os
import sys


_ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_CONF_PATH = os.path.join(_ROOT_PATH, 'config')
_LIB_PATH = os.path.join(_ROOT_PATH, 'lib')
_UTIL_PATH = os.path.join(_ROOT_PATH, 'utils')
_CONTROLLER_PATH = os.path.join(_ROOT_PATH, 'controller')
_TEMPLATE = os.path.join(_ROOT_PATH, 'template/')
_SCRIPT = os.path.join(_ROOT_PATH, 'script/')
_SCRIPT_FONT = os.path.join(_SCRIPT, 'font/')

_path = ()
_path += _CONF_PATH, _LIB_PATH, _UTIL_PATH, _CONTROLLER_PATH, _TEMPLATE, _SCRIPT
map(sys.path.append, _path)
