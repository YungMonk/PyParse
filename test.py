#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import re
import json
from utils import strings

if __name__ == '__main__':

    filename = os.getcwd() + '/test/data/resume/zhaopin/6.html'
    with open(filename, 'r') as f:
        fileContext = f.read()
        f.close()

    post_args = strings.rpc_params({
        'c': 'apis/logic_parse',
        'm': 'parsers_engine',
        'p': {
            'site_id': 1,
            'type': 1,
            'body': fileContext,
        }
    })
    print(json.dumps(post_args, ensure_ascii=False))
