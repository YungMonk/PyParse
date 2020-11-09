#! /bin/bash/python3.8
# -*- coding:utf8 -*-

import json
import os
import re
import sys
import traceback

import config.constant as pather


class load_func(object):
    """
        loading the method by linux-channel model.
    """

    def __init__(self, func):
        self.func = func

    def __ror__(self, inputs):
        return self.func(inputs)


class configer(object):
    """
        This class will hold configurations and registered setups(functions)
        It can determine when to setup them
    """
    config = {}
    setups = []

    def register(self, **deco):
        def foo(func):
            location = deco.get('look')
            level = deco.get('level', 99999)
            self.setups.append({
                'func': func,
                'location': location,
                'level': level
            })
            return func

        return foo

    def setup(self, own_cfg, onlevel=0):
        """
            Call all(or specific level) setup functions which registered via using
            "Configer.register" decorator.
            If "onlevel" has been set, only the matched setup functions will be
            loaded(or hot reloaded).
            BE CAREFUL! The registered setup function shall apply reload logic in case
            of a runtime-hot-reloaded callback hit.
        """
        self.setups.sort(key=lambda x: x['level'])
        self.config.update(own_cfg)

        for s in self.setups:
            func = s['func']
            location = s['location']
            try:
                if location:
                    func(self.config[location])
                else:
                    func()
            except ValueError:
                traceback.print_exc()
                sys.exit(1)

    def load(self, full_path):
        cfg = {}
        with open(full_path, 'r') as f:
            raw = f.read()
            # 去掉多行注释
            raw_escape_comment = re.sub(r'[\s\t\n]+/\*[\s\S]+?\*/', '', raw)
            cfg = json.loads(raw_escape_comment)

        if cfg.get('$includes'):
            for include in cfg['$includes']:
                include_conf_file = os.path.join(pather.CONF_PATH, include)
                icfg = self.load(include_conf_file)
                cfg.update(icfg)

        return cfg


instance = configer()
