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
    # re.findall(r'(\d{1,2})[-,/,月](\d{1,2})', args['created'])


    filename = os.getcwd() + '/test/data/position/zhaopin/1.html'
    with open(filename, 'r') as f:
        fileContext = f.read()
        f.close()

    post_args = strings.rpc_params({
        'c': 'apis/logic_parse',
        'm': 'parsers_engine',
        'p': {
            'site_id': 1,
            'type': 2,
            'body': fileContext,
        }
    })
    print(json.dumps(post_args, ensure_ascii=False))
