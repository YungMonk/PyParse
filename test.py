#!/usr/bin/env python3.8.2
# -*- coding:utf-8 -*-

import os
import re
import json
import time

from utils import strings


if __name__ == '__main__':
    args = {'time':'2020-07','is_grad':1, 'degree':1} 
    

    print(args)

    # filename = os.getcwd() + '/test/data/resume/qzrc/1.html'
    # with open(filename, 'r') as f:
    #     fileContext = f.read()
    #     f.close()

    # post_args = strings.rpc_params({
    #     'c': 'apis/logic_parse',
    #     'm': 'parsers_engine',
    #     'p': {
    #         'site_id': 10011,
    #         'type': 1,
    #         'body': fileContext,
    #     }
    # })
    # print(json.dumps(post_args, ensure_ascii=False))
