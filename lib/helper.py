#!/usr/bin/python3.8
# -*- coding: utf-8 -*-

import re
import time

from lxml import etree

from lib.configer import conf
from utils import strings


# 回调函数处理
async def optimize(args, funcs=[]):

    for func in funcs:
        if not args:
            return args

        if func == 'call_prev':
            continue

        params = []
        if (tmp := re.search(r'(.*?)\[(.*)\],(\d+),(\d+)', func)):
            call_info = tmp.groups()

            params = call_info[1].split(',')
            params = [placeholder(str(x)) for x in params]
            func = getattr(__import__('lib.helper', fromlist='helper'), call_info[0])
            cres = func(args, *params)

            idx_1 = int(call_info[2])
            idx_2 = int(call_info[3])
            args = ""
            if idx_1 < len(cres):
                tmp = cres[idx_1]
                if idx_2 < len(tmp):
                    args = tmp[idx_2]

        elif (tmp := re.search(r'(.*)\[(.*)\],(\d+)', func)):
            call_info = tmp.groups()

            if call_info[0] == "preg_match" or call_info[0] == "preg_match_all":
                params.append(call_info[1])
            else:
                params = call_info[1].split(',')
            
            params = [placeholder(str(x)) for x in params]

            func = getattr(__import__('lib.helper', fromlist='helper'), call_info[0])
            cres = func(args, *params)

            idx_1 = int(call_info[2])
            if idx_1 < len(cres):
                args = cres[idx_1]
        elif (tmp :=re.search(r'(.*?)\[(.*)\]', func)):
            call_info = tmp.groups()

            params = call_info[1].split(',')
            params = [placeholder(str(x)) for x in params]
            func = getattr(__import__('lib.helper', fromlist='helper'), call_info[0])

            args = func(args, *params)
        elif (tmp := re.search(r'(.*),(\d+)', func)):
            call_info = tmp.groups()

            func = getattr(__import__('lib.helper', fromlist='helper'), call_info[0])
            cres = func(args)

            idx_1 = int(call_info[1])
            args = ""
            if idx_1 < len(cres):
                args = cres[idx_1]
        elif (tmp := re.search(r'(\S+)', func)):
            call_info = tmp.groups()

            func = getattr(__import__('lib.helper', fromlist='helper'), call_info[0])
            if call_info[0] == "handle_address_city":
                args = await func(args)
            else :
                args = func(args)

    return args


# 占位符还原
def placeholder(str=''):
    return str.replace('@或@', '|').replace('逗号', ',').replace('左中括号', '[').replace('右中括号', ']').replace('右括号', '(').replace('左括号', ')').replace('\\n', '\n')


# 中文数字转阿拉伯数字
def cn2dig(cn):
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
    ldig = []  # 临时数组
 
    while lcn:
        cndig = lcn.pop()
 
        if cndig in CN_UNIT:
            unit = CN_UNIT.get(cndig)
            if unit == 10000:
                ldig.append('w')  # 标示万位
                unit = 1
            elif unit == 100000000:
                ldig.append('y')  # 标示亿位
                unit = 1
            elif unit == 1000000000000:  # 标示兆位
                ldig.append('z')
                unit = 1
            continue
        else:
            dig = CN_NUM.get(cndig)
            if unit:
                dig = dig * unit
                unit = 0
 
            ldig.append(dig)
 
    if unit == 10:  # 处理10-19的数字
        ldig.append(10)
 
    ret = 0
    tmp = 0
 
    while ldig:
        x = ldig.pop()
 
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
   

# 去除字符串首尾处的空白字符（或者其他字符）
def trim(args="", *extra):
    return strings.trim(args, *extra)


# 去除html文本中的所有标签
def strip_tags(args="", *extra):
    return strings.strip_tags(args)


# 字符串分割
def explode(args="", *extra):
    return args.split(extra[0] if len(extra) else " ")


# 正则使用
def preg_match(args="", *extra):
    if len(extra) and extra[0] and (matches := re.search(extra[0], args)):
        return matches.groups()


# 正则全匹配
def preg_match_all(args="", *extra):
    if len(extra) and extra[0] and (matches := re.findall(extra[0], args)):
        return matches


# 正则替换
def preg_replace(args="", *extra):
    if len(extra) and extra[0]:
        return re.sub(extra[0], extra[1] if len(extra) > 1 else "", args)
    else:
        return args


# 单位（千）转换
def k2k(args="", *extra):
    return strings.salary_to_k(args)


# 单位（万）转换
def w2k(args="", *extra):
    return strings.salary_to_k(args, 'W')


# xpath处理
def handle_xpath(args="", *extra):
    return etree.HTML(args).xpath(placeholder(extra[0]))


# 匹配出生日
def handle_birthday(args="", *extra):
    string = ""
    if (matchObj := re.search(r'([1-2]{1}[0,9]{1}[0-9]{2})\s*(年|-|\.){1}\s*([0,1]{0,1}[0-9]{1})\s*(月|-|\.){1}\s*([0-3]{0,1}[0-9]{1})',args)):
        string = "{}年{}月{}日".format(matchObj.group(1), matchObj.group(3), matchObj.group(5))
    elif (matchObj := re.search(r'([1-2]{1}[0,9]{1}[0-9]{2})\s*(年|-|\.){1}\s*([0,1]{0,1}[0-9]{1})', args)):
        string = "{}年{}月".format(matchObj.group(1), matchObj.group(3))
    elif (matchObj := re.search(r'(\d+)\s*岁', args)):
        string = "{}年".format(time.localtime(time.time()).tm_year - int(matchObj.group(1)))
    return string if string else args


# 匹配年龄
def handle_age(args="", *extra):
    string = ""
    if (matchObj := re.search(r'(\d+)\s*岁', args)):
        string = matchObj.group(1)
    
    return string


# 匹配性别
def handle_gender(args="", *extra):
    sexs = {'男': 'M', '女': 'F', 'male': 'M', 'female': 'F', '1': 'M', '0': 'F'}
    if (isMatch := re.search(r'(男|女|male|female)', args)):
        return sexs[isMatch.group(1)]


# 匹配学历
def handle_degree(args="", *extra):
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
    if (isMatch := re.search(r'(初中|高中|中专|中技|专科|大专|本科|硕士|博士|MBA)', args)):
        return degrees[isMatch.group(1)]
    else:
        return 99


# 语言匹配
def handle_langue(args="", *extra):
    if (isMatch := re.search(r'(英语|日语|俄语|阿拉伯语|法语|德语|西班牙语|葡萄牙语|意大利语|韩语/朝鲜语|普通话|粤语|闽南语|上海话|其它)', args)):
        return isMatch.group(1)
    else:
        return ""


# 是否最近
def handle_sofar(args="", *extra):
    if 'start_time' in args and 'end_time' in args and args['end_time'] == '':
        args['so_far'] = 'Y'
    else:
        args['so_far'] = 'N'
    return args


# 婚姻状态
def handle_marital(args="", *extra):
    marital = {'已婚': 'Y', '未婚': 'N', 'single': 'N', 'married': 'Y', 'unmarried': 'N'}
    if (isMatch := re.search(r'(已婚|未婚|single|married|unmarried)', args)):
        return marital[isMatch.group(1)]
    else:
        return "U"


# 工作经验
def handle_experience(args="", *extra):
    result = ["", ""]
    if (isMatch := re.search(r'(\d+)年以下(工作经验|经验)*', args)):
        # 10年以下工作经验，8年以下经验
        result[1] = isMatch.group(1)
    elif (isMatch := re.search(r'(\d+)(\s|\.0)*年以上(工作经验|经验)*', args)):
        # 10以上工作经验，10.0年以上工作经验，8年以上经验
        result[0] = isMatch.group(1)
    elif (isMatch := re.search(r'(\S+)年以上', args)):
        # 十年以上工作经验
        result[0] = cn2dig(isMatch.group(1))
    elif (isMatch := re.search(r'(\d+)-(\d+)年(工作经验|经验)*', args)):
        # 8-10年工作经验，8-10年经验
        result[0] = isMatch.group(1)
        result[1] = isMatch.group(2)
    elif (isMatch := re.search(r'(\d+)年(工作经验|经验)', args)):
        # 8年工作经验
        result[1] = result[0] = isMatch.group(1)
    elif (isMatch := re.search(r'(\d+)years', args)):
        # 10years
        result[1] = result[0] = isMatch.group(1)
    elif (isMatch := re.search(r'(\d+)\s*年(?!\d)', args)):
        # 10 年，10年
        result[1] = result[0] = isMatch.group(1)
    elif (isMatch := re.search(r'(\S+)年', args)):
        # 八年
        result[1] = result[0] = cn2dig(isMatch.group(1))

    return result

 
# 处理时间
def handle_time(args="", *extra):
    matches = re.findall(r'(\d{4}.*?\d{1,2}.{1})', re.sub(r'(\d{4}).*?(\d{1,2})','\\1年\\2月', args))
    if matches:
        return matches[0]


#  处理时间间隔
def handle_interval(args="", *extra):
    args['start_time'] = ""
    args['end_time'] = ""
    args['so_far'] = "N"

    isMatch = re.findall(r'(\d{4}.*?\d{1,2}.{1})', re.sub(r'(\d{4}).*?(\d{1,2})','\\1年\\2月', args['time']))
    if len(isMatch) == 1:
        args['start_time'] = isMatch[0]
    elif len(isMatch) == 2:
        args['start_time'] = isMatch[0] 
        args['end_time'] = isMatch[1]

    args = handle_sofar(args, *extra)

    args.pop('time','')
    return args


# 处理基本薪资
def handle_basic_salary(args="", *extra):
    args['basic_salary_from'] = ""
    args['basic_salary_to'] = ""

    if "basic_salary" in args:
        salary = args['basic_salary']
        # 年薪
        if '年' in salary and (matches := re.findall(r'(\d+\.*\d+)', salary, re.I | re.S)):
            if len(matches) == 1:
                args['basic_salary_from'] = strings.salary_to_k(matches[0], salary)
                args['basic_salary_to']   = strings.salary_to_k(matches[0], salary)
            elif len(matches) == 2:
                args['basic_salary_from'] = strings.salary_to_k(matches[0], salary)
                args['basic_salary_to']   = strings.salary_to_k(matches[1], salary)

        elif matches := re.findall(r'(\d+\.*\d+)', salary, re.I | re.S):
            if len(matches) == 1:
                args['basic_salary_from'] = strings.salary_to_k(matches[0], salary)
                args['basic_salary_to']   = strings.salary_to_k(matches[0], salary)
            elif len(matches) == 2:
                args['basic_salary_from'] = strings.salary_to_k(matches[0], salary)
                args['basic_salary_to']   = strings.salary_to_k(matches[1], salary)

    return args


# 处理期望薪资
def handle_expect_salary(args="", *extra):
    args['expect_salary_from'] = ""
    args['expect_salary_to'] = ""
    args['expect_annual_salary_from'] = ""
    args['expect_annual_salary_to'] = ""
    args['expect_hour_salary_from'] = ""
    args['expect_hour_salary_to'] = ""
    args['expect_day_salary_from'] = ""
    args['expect_day_salary_to'] = ""

    if "expect_salary" in args:
        salary = args['expect_salary']
        # 年薪
        if '年' in salary and (matches := re.findall(r'(\d+\.*\d+)', salary, re.I | re.S)):
            if len(matches) == 1:
                args['expect_annual_salary_from'] = strings.salary_to_k(matches[0], salary)
                args['expect_annual_salary_to']   = strings.salary_to_k(matches[0], salary)
            elif len(matches) == 2:
                args['expect_annual_salary_from'] = strings.salary_to_k(matches[0], salary)
                args['expect_annual_salary_to']   = strings.salary_to_k(matches[1], salary)

            args['expect_salary_from'] = '%.2f' % (args['expect_annual_salary_from']/12)
            args['expect_salary_to']   = '%.2f' % (args['expect_annual_salary_to']/12)
        elif matches := re.findall(r'(\d+\.*\d+)', salary, re.I | re.S):
            if len(matches) == 1:
                args['expect_salary_from'] = strings.salary_to_k(matches[0], salary)
                args['expect_salary_to']   = strings.salary_to_k(matches[0], salary)
            elif len(matches) == 2:
                args['expect_salary_from'] = strings.salary_to_k(matches[0], salary)
                args['expect_salary_to']   = strings.salary_to_k(matches[1], salary)

    return args


# 清洗技能
def wash_skill(args, *extra):
    parrten = r'(英语|日语|俄语|阿拉伯语|法语|德语|西班牙语|葡萄牙语|意大利语|韩语|朝鲜语|普通话|粤语|闽南语|上海话|其它)'
    if "name" in args and re.findall(parrten, args['name'], re.S | re.I):
        return None
    else:
        return args


# 清洗语言
def wash_langue(args, *extra):
    parrten = r'(英语|日语|俄语|阿拉伯语|法语|德语|西班牙语|葡萄牙语|意大利语|韩语|朝鲜语|普通话|粤语|闽南语|上海话|其它)'
    if "name" in args and re.findall(parrten, args['name'], re.S | re.I):
        return args
    else:
        return None


# 清洗名称为空的
def wash_name_null(args, *extra):
    if "name" in args and args['name']:
        return args
    elif "corporation_name" in args and args['corporation_name']:
        return args
    elif "school_name" in args and args['school_name']:
        return args
    else:
        return None


""""异步方法调用"""
# 户籍，现居住地相关 
async def handle_address_city(args, *extra) -> dict:
    if not isinstance(args, dict):
        return args
    else:
        # 籍贯所在地的市级ID
        args['native_place'] = ""
        # 籍贯所在地的省级ID
        args['native_place_province'] = ""
        # 户口所在地的市级ID
        args['account'] = ""
        # 户口所在地的省级ID
        args['account_province'] = ""
        # 当前所在地的市级id
        args['address'] = ""
        # 当前所在地的省级id
        args['address_province'] = ""

        import json
        if "account_address" in args and args['account_address']:
            args['account'] = await http_curl(url=conf.config.get('rcp_service', None)['gsystem'], city=args['account_address'])
        if "address_detail" in args and args['address_detail']:
            args['address'] = await http_curl(url=conf.config.get('rcp_service', None)['gsystem'], city=args['address_detail'])
                
        
        args['account_district'] = args['account'] # 灵活用工使用
        args['address_district'] = args['address'] # 灵活用工使用

    return args


async def http_curl(**kwargs):
    if "city" not in kwargs or not kwargs['city']:
        return ""

    if "url" not in kwargs or not kwargs['url']:
        return ""

    from tornado.httpclient import AsyncHTTPClient,HTTPRequest,HTTPError
    import json
    
    http_client = AsyncHTTPClient()
    http_request = HTTPRequest(
        url=kwargs['url'],
        method='POST',
        headers={
            "Content-type":"application/json;charset='utf-8'",
            "Accept":"application/json",
            "Cache-Control:":"no-cache",
            "Pragma":"no-cache",
            "Connection":"Keep-Alive"
        },
        body=json.dumps(strings.rpc_params({
            'c':'Logic_region',
            'm':'city_ids',
            'p':kwargs['city'],
        })),
    )

    result = ""
    try:
        response = await AsyncHTTPClient().fetch(http_request)
        respdata = json.loads(response.body)
        if 'response' in respdata and 'err_no' in respdata['response'] and not respdata['response']['err_no']:
            result = respdata['response']['results']
    except HTTPError as e:
        # HTTPError is raised for non-200 responses; the response
        # can be found in e.response.
        print("Error: " + str(e))
    except Exception as e:
        # Other errors are possible, such as IOError.
        print("Error: " + str(e))
    finally :
        http_client.close()

    return result
