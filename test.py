#!/usr/bin/env python3.8.2
# -*- coding:utf-8 -*-

import os,re
import json
import time

from utils import strings


if __name__ == '__main__':
    matches = re.findall(r'(\d{4}年)', '2010年获得')
    print(matches[0])


    # filename = os.getcwd() + '/test/data/resume/597/zh1_1.html.html'
    # with open(filename, 'r') as f:
    #     fileContext = f.read()
    #     f.close()
    # post_args = strings.rpc_params({
    #     'c': 'apis/logic_parse',
    #     'm': 'parsers_engine',
    #     'p': {
    #         'site_id': 10010,
    #         'type': 1,
    #         'body': fileContext,
    #     }
    # })
    # print(json.dumps(post_args, ensure_ascii=False))
