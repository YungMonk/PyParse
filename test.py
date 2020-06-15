#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import re
import json
import sys
import string
from utils import strings

if __name__ == '__main__':
    # arr =  {"a":"10", "b":"8", "c":""}
    # arr = [strings.atoi(x) for x in arr.values()]
    # print(max(arr))
    # sys.exit(0)

    filename = os.getcwd() + '/test/data/resume/liepin/赵女士.html'
    with open(filename, 'r') as f:
        fileContext = f.read()
        f.close()

    post_args = strings.rpc_params({
        'c': 'apis/logic_parse',
        'm': 'parsers_engine',
        'p': {
            'site_id': 3,
            'type': 1,
            'body': fileContext,
        }
    })
    print(json.dumps(post_args, ensure_ascii=False))
