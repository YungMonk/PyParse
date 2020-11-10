#! /usr/bin/python3.8
# -*- coding:utf-8 -*-
import re
import socket
import time
from html.parser import HTMLParser
from typing import (Any, )


class MLStripper(HTMLParser):
    def error(self, message):
        pass

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def handle_entityref(self, name):
        self.fed.append('&%s;' % name)

    def handle_charref(self, name):
        self.fed.append('&#%s;' % name)

    def get_data(self):
        return ''.join(self.fed)


def _strip_once(value: str):
    """
    Internal tag stripping utility used by strip_tags.
    """
    s = MLStripper()
    s.feed(value)
    s.close()
    return s.get_data()


def strip_tags(value: str = "") -> str:
    """
        Return the given HTML with all tags stripped.
        Note: in typical case this loop executes _strip_once once. Loop condition
        is redundant, but helps to reduce number of executions of _strip_once.
    """
    value = str(value)
    while '<' in value and '>' in value:
        new_value = _strip_once(value)
        if value.count('<') == new_value.count('<'):
            # _strip_once wasn't able to detect more tags.
            break
        value = new_value
    return value


def trim(args: str = "", *extra: Any) -> str:
    """
        Strip whitespace (or other characters) from the beginning and end of a string
    """
    return args.strip(extra[0] if len(extra) else " \t\n\r\0\x0B")


def host_name() -> str:
    """
        Return the current host name.
    """

    return socket.gethostname()


def host_address() -> str:
    """
        Return the current host address.
    """
    s: socket = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def net_used(port: int, ip='127.0.0.1') -> bool:
    """
        check port is used.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, port))
        return True
    except ConnectionError:
        return False
    finally:
        s.close()


def rpc_params(request: dict, **header: Any) -> dict:
    """
        merge the params for rpc request.
    """

    ip = host_address()
    params = {
        "header": {
            'provider': 'grab',
            'ip': ip,
            'appid': 10,
            'user_ip': ip,
            'uid': 10,
            'product_name': 'cv_parser',
        },
        "request": {}
    }

    params['header'] = dict(params['header'], **header)
    params['request'] = dict(params['request'], **request)

    return params


def salary_to_k(args: str, flag: str = "") -> str:
    """
        Salary unit converted to thousand.
    """
    if '.' in args:
        args = float(args)
    else:
        args = int(args)

    if '千' in flag or 'K' in flag or 'k' in flag:
        return '%.2f' % args
    elif '万' in flag or 'W' in flag or 'w' in flag:
        return '%.2f' % (args * 10)
    else:
        return '%.2f' % (args * 0.001)


def cn2dig(cn: str):
    """
        中文数字转拉丁字母
    """
    CN_NUM = {
        u'〇': 0,
        u'一': 1,
        u'二': 2,
        u'三': 3,
        u'四': 4,
        u'五': 5,
        u'六': 6,
        u'七': 7,
        u'八': 8,
        u'九': 9,

        u'零': 0,
        u'壹': 1,
        u'贰': 2,
        u'叁': 3,
        u'肆': 4,
        u'伍': 5,
        u'陆': 6,
        u'柒': 7,
        u'捌': 8,
        u'玖': 9,

        u'貮': 2,
        u'两': 2,
    }

    CN_UNIT = {
        u'十': 10,
        u'拾': 10,
        u'百': 100,
        u'佰': 100,
        u'千': 1000,
        u'仟': 1000,
        u'万': 10000,
        u'萬': 10000,
        u'亿': 100000000,
        u'億': 100000000,
        u'兆': 1000000000000,
    }

    lcn = list(cn)
    unit = 0  # 当前的单位
    tmp_set = []  # 临时数组

    while lcn:
        china_num = lcn.pop()

        if china_num in CN_UNIT:
            unit = CN_UNIT.get(china_num)
            if unit == 10000:
                tmp_set.append('w')  # 标示万位
                unit = 1
            elif unit == 100000000:
                tmp_set.append('y')  # 标示亿位
                unit = 1
            elif unit == 1000000000000:  # 标示兆位
                tmp_set.append('z')
                unit = 1
            continue
        else:
            dig = CN_NUM.get(china_num)
            if unit:
                dig = dig * unit
                unit = 0

            tmp_set.append(dig)

    if unit == 10:  # 处理10-19的数字
        tmp_set.append(10)

    ret = 0
    tmp = 0

    while tmp_set:
        x = tmp_set.pop()

        if x == 'w':
            tmp *= 10000
            ret += tmp
            tmp = 0

        elif x == 'y':
            tmp *= 100000000
            ret += tmp
            tmp = 0

        elif x == 'z':
            tmp *= 1000000000000
            ret += tmp
            tmp = 0

        else:
            tmp += x

    ret += tmp
    return ret


def atoi(stg: str = "") -> int:
    """
    :type stg: str
    :rtype: int
    """
    s = stg.lstrip()
    if not s:
        return 0
    a = s[0]
    num = 0
    if a.isdigit():
        flag = 1
        num = int(a)
    elif a == '+':
        flag = 1
    elif a == '-':
        flag = -1
    else:
        return 0
    for i in range(1, len(s)):
        j = s[i]
        if j.isdigit():
            num = num * 10 + int(j)
        else:
            break
    num = flag * num
    int_max = 2 ** 31 - 1
    int_min = -2 ** 31
    if num > int_max:
        return int_max
    elif num < int_min:
        return int_min
    else:
        return num


def get_val_by_keys(keys: str = "", ctx=None) -> Any:
    r"""get a value for dict or list by a string

    >>> dt = {
    >>>     "name": {
    >>>         "real": "yang",
    >>>         "last": "monk",
    >>>     }
    >>>     "work": [
    >>>         1, 2
    >>>     ]
    >>> }
    >>> print(get_val_by_keys('work.0', dt))
    >>> 1

    """
    if ctx is None:
        ctx = {}
    arr_key = keys.split(".")
    for key in arr_key:
        if isinstance(ctx, list) and key.isdigit():
            idx = int(key)
            if len(ctx) < idx:
                return ""
            else:
                ctx = ctx[idx]
        elif isinstance(ctx, dict):
            if key not in ctx:
                return ""
            else:
                ctx = ctx[key]
        else:
            return ""

    return ctx


def str_to_time(args: str = "") -> int:
    """时间转时间戳"""
    if matches := re.findall(r'(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})', args, re.I | re.S):
        timeArray = time.strptime(
            "{}/{}/{}".format(matches[0][0], matches[0][1], matches[0][2]), "%Y/%m/%d"
        )
        # 转换成时间戳
        return int(time.mktime(timeArray))

    if matches := re.findall(r'(\d{4}).*?(\d{1,2})', args, re.I | re.S):
        # 转换成时间数组
        timeArray = time.strptime(
            "{}/{}".format(matches[0][0], matches[0][1]), "%Y/%m"
        )
        # 转换成时间戳
        return int(time.mktime(timeArray))


if __name__ == "__main__":
    dict1 = {"name": "owen", "age": 18, "height": 150}
    dict2 = {"birthday": "1999-11-22", "height": 180}

    new_dict = dict(dict1, **dict2)
    print(new_dict)
