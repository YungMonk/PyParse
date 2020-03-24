import re, time


# 回调函数处理
def optimize(args, funcs=[]):
    funcMaps = {
        "trim": trim,
        "explode": explode,
        "preg_match": preg_match,
        "handle_birthday": handle_birthday,
        "handle_gender": handle_gender,
        "handle_degree": handle_degree,
    }

    if len(funcs) == 0:
        return args
    for func in funcs:
        if 'func' not in func or len(func['func']) == 0:
            continue

        extra = {}
        if 'extra' in func:
            extra = func['extra']
        args = funcMaps[func['func']](args, **extra)

    return args


# 去除字符串首尾处的空白字符（或者其他字符）
def trim(args="", **extra):
    character_mask = " \t\n\r\0\x0B"
    if 'param' in extra and len(extra['param']):
        character_mask = extra['param'][0]
    return args.strip(character_mask)


# 字符串分割
def explode(args="", **extra):
    delimiter = " "
    if 'param' in extra and len(extra['param']):
        delimiter = extra['param'][0]
    return args.split(delimiter)[1]


# 正则使用
def preg_match(args="", **extra):
    if 'param' in extra and len(extra['param']):
        pattern = extra['param'][0]
    pattern = re.compile(pattern)
    if 'index' in extra and len(extra['index']):
        return pattern.search(args).group(extra['index'][0])


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
