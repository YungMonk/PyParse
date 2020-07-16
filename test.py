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
    args = """
    下面是一些测试实例:
history: v1.0 正则表达式测试工具上线
         v1.1 2012-03-25 修复高亮偏移错位的问题
         v1.2 2014-06-15 增加生成程序代码的功能
         v1.3 2014-09-04 增加java代码的生成，修正邮箱的匹配
             1. 截至目前为止，最长域名后缀 .cancerresearch
         v1.4 2016-03-12 重写代码生成引擎，解决生成的bug
         v1.5 2017-10-29 彻底重写测试功能解决文本过长时产生的高亮bug
         v1.6 2020-07-12 增加dart语言的正则生成
notice: 由于我们使用的是js的正则引擎，所以暂时还不能支持逆序环视
demo@qq.com
tool-lu@vip.qq.com
tool+lu@gmail.com
demo@live.com
127.0.0.1
http://tool.lu/
https://tool.lu/
123456789012345
16:09:22
    """
    isMatch = re.findall(r'(\d{1,2})[-,/,月](\d{1,2})', args)
    print("-".join(isMatch[0]))
    print(time.localtime().tm_year)
    # filename = os.getcwd() + '/test/data/resume/tianjihr/3.txt'
    # with open(filename, 'r') as f:
    #     fileContext = f.read()
    #     f.close()

    # post_args = strings.rpc_params({
    #     'c': 'apis/logic_parse',
    #     'm': 'parsers_engine',
    #     'p': {
    #         'site_id': 10023,
    #         'type': 1,
    #         'body': fileContext,
    #     }
    # })
    # print(json.dumps(post_args, ensure_ascii=False))
