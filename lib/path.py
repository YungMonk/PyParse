#! /bin/bash/python3.8
# -*- coding:utf8 -*

import os
import sys


_ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_CONF_PATH = os.path.join(_ROOT_PATH, 'config')
_LIB_PATH = os.path.join(_ROOT_PATH, 'lib')
_UTIL_PATH = os.path.join(_ROOT_PATH, 'utils')
_CONTROLLER_PATH = os.path.join(_ROOT_PATH, 'controller')

_path = ()
_path += _CONF_PATH, _LIB_PATH, _UTIL_PATH
map(sys.path.append, _path)
