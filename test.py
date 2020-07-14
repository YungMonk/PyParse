#!/usr/bin/env python3.8.2
# -*- coding:utf-8 -*-

import os
import re
import json
import time
from utils import strings
if __name__ == '__main__':
    arr = [
      "读书",
      "逛技术论坛"
    ]

    print(",".join(arr))

    # filename = os.getcwd() + '/test/data/resume/shixiseng/1.txt'
    # with open(filename, 'r') as f:
    #     fileContext = f.read()
    #     f.close()

    # post_args = strings.rpc_params({
    #     'c': 'apis/logic_parse',
    #     'm': 'parsers_engine',
    #     'p': {
    #         'site_id': 45,
    #         'type': 1,
    #         'body': fileContext,
    #     }
    # })
    # print(json.dumps(post_args, ensure_ascii=False))
