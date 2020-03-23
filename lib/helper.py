
import re

# 回调函数处理
def optimize(strs, funcs=[]):
    funcMaps = {
        "trim":trim,
        "explode":explode,
        "preg_match":preg_match,
    }

    if len(funcs) == 0:
        return strs
    for func in funcs:
        if 'func' not in func or len(func['func']) == 0:
            continue

        extra = {}
        if 'extra' in func:
            extra = func['extra']
        strs = funcMaps[func['func']](strs, **extra)

    return strs

# 去除字符串首尾处的空白字符（或者其他字符）
def trim(string="", **extra):
    character_mask = " \t\n\r\0\x0B"
    if 'param' in extra and len(extra['param']):
        character_mask = extra['param'][0]
    return string.strip(character_mask)

# 字符串分割
def explode(string="", **extra):
    delimiter=" "
    if 'param' in extra and len(extra['param']):
        delimiter = extra['param'][0]
    return string.split(delimiter)[1]
    
def preg_match(string="", **extra):
    if 'param' in extra and len(extra['param']):
        pattern = extra['param'][0]
    pattern = re.compile(pattern)
    if 'index' in extra and len(extra['index']):
        return pattern.match(string).group(extra['index'][0])