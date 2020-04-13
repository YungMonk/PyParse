import re
import time
from lxml import etree
from django.utils.html import strip_tags as st


# 回调函数处理
def optimize(args, funcs=[]):
    funcMaps = {
        "trim": trim,
        "strip_tags": strip_tags,
        "explode": explode,
        "preg_match": preg_match,
        "preg_match_all": preg_match_all,
        "preg_replace": preg_replace,
        "handle_xpath": handle_xpath,
        "handle_birthday": handle_birthday,
        "handle_gender": handle_gender,
        "handle_degree": handle_degree,
    }

    for func in funcs:
        if func == 'call_prev':
            continue

        cbackinfo = {"func": "", "param": []}

        tmp_1 = re.search(r'(.*?)\[(.*)\],(\d+),(\d+)', func)
        tmp_2 = re.search(r'(.*)\[(.*)\],(\d+)', func)
        tmp_3 = re.search(r'(.*?)\[(.*)\]', func)
        # print(func,tmp_1,tmp_2,tmp_3)
        if tmp_1:
            call_info = tmp_1.groups()
            cbackinfo["func"] = call_info[0]
            cbackinfo["param"] = call_info[1].split(',')
            cres = funcMaps[cbackinfo['func']](args, **cbackinfo)
            idx_1 = int(call_info[2])
            idx_2 = int(call_info[3])
            args = ""
            if idx_1 < len(cres):
                tmp = cres[idx_1]
                if idx_2 < len(tmp):
                    args = tmp[idx_2]
        elif tmp_2:
            call_info = tmp_2.groups()
            cbackinfo["func"] = call_info[0]
            if call_info[0] == "preg_match" or call_info[0] == "preg_match_all":
                cbackinfo["param"].append(call_info[1])
            else:
                cbackinfo["param"] = call_info[1].split(',')
            cres = funcMaps[cbackinfo['func']](args, **cbackinfo)
            idx_1 = int(call_info[2])
            args = ""
            if idx_1 < len(cres):
                args = cres[idx_1]
        elif tmp_3:
            call_info = tmp_3.groups()
            cbackinfo["func"] = call_info[0]
            cbackinfo["param"] = call_info[1].split(',')
            args = funcMaps[cbackinfo['func']](args, **cbackinfo)
        else:
            args = funcMaps[func](args, **cbackinfo)

    return args


def placeholder(str=''):
    return str.replace('@或@', '|').replace('逗号', ',').replace('左中括号', '[').replace(
        '右中括号', ']').replace('右括号', '(').replace('左括号', ')').replace('\\n', '\n')


# 去除字符串首尾处的空白字符（或者其他字符）
def trim(args="", **extra):
    character_mask = " \t\n\r\0\x0B"
    if 'param' in extra and len(extra['param']):
        character_mask = extra['param'][0]
    return args.strip(character_mask)


# 去除html文本中的所有标签
def strip_tags(args="", **extra):
    return st(args)


# 字符串分割
def explode(args="", **extra):
    delimiter = " "
    if 'param' in extra and len(extra['param']):
        delimiter = extra['param'][0]
    return args.split(delimiter)


# 正则使用
def preg_match(args="", **extra):
    if 'param' in extra and len(extra['param']):
        pattern = extra['param'][0]
        return re.search(pattern, args).groups()


def preg_match_all(args="", **extra):
    if 'param' in extra and len(extra['param']):
        pattern = extra['param'][0]
        print(pattern, args)
        return re.findall(pattern, args)


# 正则替换
def preg_replace(args="", **extra):
    if 'param' in extra and len(extra['param']):
        pattern = extra['param'][0]
        if len(extra['param']) > 1:
            replace = extra['param'][1]
        else:
            replace = ""
        return re.sub(pattern, replace, args)


def handle_xpath(args="", **extra):
    etreehtml = etree.HTML(args)
    return etreehtml.xpath(placeholder(extra['param'][0]))

# 匹配出生日


def handle_birthday(args="", **extra):
    string = ""
    matchObj = re.search(
        r'([1-2]{1}[0,9]{1}[0-9]{2})\s*(年|-|\.){1}\s*([0,1]{0,1}[0-9]{1})\s*(月|-|\.){1}\s*([0-3]{0,1}[0-9]{1})',
        args)
    if matchObj:
        string = "{}年{}月{}日".format(matchObj.group(1), matchObj.group(3),
                                    matchObj.group(5))
    elif re.search(
            r'([1-2]{1}[0,9]{1}[0-9]{2})\s*(年|-|\.){1}\s*([0,1]{0,1}[0-9]{1})',
            args):
        matchObj = re.search(
            r'([1-2]{1}[0,9]{1}[0-9]{2})\s*(年|-|\.){1}\s*([0,1]{0,1}[0-9]{1})',
            args)
        string = "{}年{}月".format(matchObj.group(1), matchObj.group(3))
    elif re.search(r'(\d+)岁', args):
        matchObj = re.search(r'(\d+)岁', args)
        string = "{}年".format(
            time.localtime(time.time()).tm_year - int(matchObj.group(1)))
    return string if string else args


# 匹配性别
def handle_gender(args="", **extra):
    sexs = {'男': 'M', '女': 'F', 'male': 'M', 'female': 'F', '1': 'M', '0': 'F'}
    pattern = re.compile(r'(男|女|male|female)')
    isMatch = pattern.search(args)
    if isMatch:
        return sexs[isMatch.group(1)]


# 匹配学历
def handle_degree(args="", **extra):
    degrees = {
        '本科及以上': 1,
        '本科': 1,
        '硕士及以上': 2,
        '硕士': 2,
        '博士及以上': 3,
        '博士': 3,
        '大专及以上': 4,
        '专科': 4,
        '大专': 4,
        'MBA': 6,
        'MBA&EMBA': 6,
        'EMBA': 6,
        '博士后': 10,
        '初中': 86,
        '高中': 89,
        '高中/中专': 89,
        '中专': 90,
        '中技': 91,
        '学历不限': 99,
        '其他': 99,
        '不限': 99,
    }
    pattern = re.compile(r'(初中|高中|中专|中技|专科|大专|本科|硕士|博士|MBA)')
    isMatch = pattern.search(args)
    if isMatch:
        return degrees[isMatch.group(1)]
    else:
        return 99
