#!/usr/bin/env python3.8.2
# -*- coding:utf-8 -*-

import os
import re
import json
import time
from datetime import datetime
from utils import strings
from dateutil.relativedelta import relativedelta
if __name__ == '__main__':
    # isMatch = re.search(r'(\d+\s*)(?=人)', '上海,5-10年,本科,招1人')
    # print(isMatch[0])


    filename = os.getcwd() + '/test/data/position/lagou/lagou01.html'
    with open(filename, 'r') as f:
        fileContext = f.read()
        f.close()

    post_args = strings.rpc_params({
        'c': 'apis/logic_parse',
        'm': 'parsers_engine',
        'p': {
            'site_id': 11,
            'type': 2,
            'body': fileContext,
        }
    })

    print(json.dumps(post_args, ensure_ascii=False))
