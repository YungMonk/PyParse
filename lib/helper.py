#!/usr/bin/python3.8
# -*- coding: utf-8 -*-

from lxml import etree

import re
import time

from lib.configer import instance
from utils import strings
from lib import route

async def optimize(args, funcs=[]):
    '''
        回调函数处理
    '''

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
            if cres and idx_1 < len(cres):
                args = cres[idx_1]
            else:
                args = ""
        elif (tmp := re.search(r'(.*?)\[(.*)\]', func)):
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
            if cres and idx_1 < len(cres):
                args = cres[idx_1]
        elif (tmp := re.search(r'(\S+)', func)):
            call_info = tmp.groups()

            func = getattr(__import__('lib.helper', fromlist='helper'), call_info[0])
            # 协同方法特殊处理
            if call_info[0] in ["handle_address_city", "handle_except_citys", "handle_citys", "fetch_head"]:
                args = await func(args)
            else :
                args = func(args)

    return args


def placeholder(str=''):
    '''
        占位符还原
    '''
    return str.replace('@或@', '|').replace('逗号', ',').replace('左中括号', '[').replace('右中括号', ']').replace('右括号', '(').replace('左括号', ')').replace('\\n', '\n')


def cn2dig(cn):
    '''
        中文数字转阿拉伯数字
    '''
    return strings.cn2dig(cn)


def trim(args="", *extra):
    '''
        去除字符串首尾处的空白字符（或者其他字符）
    '''
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


# 正则分割
def handle_regualr(args="", *extra):
    if not args:
        return args
    args = re.sub('\n', '', args)
    repl = re.sub(extra[0], extra[1], args, re.I | re.S)
    _arr = repl.split(extra[2])
    preTag = '<div>' if len(extra) < 4 else extra[3]
    endTag = '</div>' if len(extra) < 5 else extra[4]
    xpath = []
    for _val in _arr:
        if not _val:
            continue
        _html = preTag + _val + endTag
        xpath.append(etree.HTML(_html))

    return xpath


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
    elif (matchObj := re.search(r'(\d{2})', args)):
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


def handle_basic_experience(args="", *extra):
    args["work_experience"]= ""
    args["working_seniority_from"]= ""
    args["working_seniority_to"]= ""

    if "experience" not in args or not args["experience"]:
        return args

    experience = args["experience"]

    if (isMatch := re.search(r'(\d+)年以下(工作经验|经验)*', experience)):
        # 10年以下工作经验，8年以下经验
        args["working_seniority_to"] = isMatch.group(1)
        args["work_experience"] = args["working_seniority_to"]
    elif (isMatch := re.search(r'(\d+)(\s|\.0)*年以上(工作经验|经验)*', experience)):
        # 10以上工作经验，10.0年以上工作经验，8年以上经验
        args["working_seniority_from"] = isMatch.group(1)
        args["work_experience"] = args["working_seniority_from"]
    elif (isMatch := re.search(r'(\S+)年以上', experience)):
        # 十年以上工作经验
        args["working_seniority_from"] = cn2dig(isMatch.group(1))
        args["work_experience"] = args["working_seniority_from"]
    elif (isMatch := re.search(r'(\d+)-(\d+)年(工作经验|经验)*', experience)):
        # 8-10年工作经验，8-10年经验
        args["working_seniority_from"] = isMatch.group(1)
        args["working_seniority_to"] = isMatch.group(2)
        args["work_experience"] = args["working_seniority_to"]
    elif (isMatch := re.search(r'(\d+)年(工作经验|经验)', experience)):
        # 8年工作经验
        args["working_seniority_to"] = isMatch.group(1)
        args["working_seniority_from"] = args["working_seniority_to"]
        args["work_experience"] = args["working_seniority_to"]
    elif (isMatch := re.search(r'(\d+)years', experience)):
        # 10years
        args["working_seniority_to"] = isMatch.group(1)
        args["working_seniority_from"] = args["working_seniority_to"]
        args["work_experience"] = args["working_seniority_to"]
    elif (isMatch := re.search(r'(\d+)\s*年(?!\d)', experience)):
        # 10 年，10年
        args["working_seniority_to"] = isMatch.group(1)
        args["working_seniority_from"] = args["working_seniority_to"]
        args["work_experience"] = args["working_seniority_to"]
    elif (isMatch := re.search(r'(\S+)年', experience)):
        # 八年
        args["working_seniority_to"] = cn2dig(isMatch.group(1))
        args["working_seniority_from"] = args["working_seniority_to"]
        args["work_experience"] = args["working_seniority_to"]

    return args


# 当前状态
def handle_current_status(args="", *extra):
    status = 0
    if re.search(r'在岗|在职|机会', args, re.S|re.I):
        status = 3
    elif re.search(r'离职|找工作', args, re.S|re.I):
        status = 1

    return status


# 政治背景
def handle_political(args="", *extra) -> str:
    parrten = r'(中共党员|预备党员|团员|民主党派|无党派人士|群众|其他)'
    if matches := re.findall(parrten, args, re.S | re.I):
        return matches[0]
    else:
        return ""

 
# 处理时间
def handle_time(args="", *extra):
    matches = re.findall(r'(\d{4}.*?\d{1,2}.{1})', re.sub(r'(\d{4}).*?(\d{1,2})','\\1年\\2月', args))
    if matches:
        return matches[0]


# 处理时间间隔
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
        if '年' in salary and (matches := re.findall(r'(\d+\.*\d+)', salary, re.I | re.S)):
        # 年薪
            if len(matches) == 1:
                args['expect_annual_salary_from'] = strings.salary_to_k(matches[0], salary)
                args['expect_annual_salary_to']   = strings.salary_to_k(matches[0], salary)
            elif len(matches) == 2:
                args['expect_annual_salary_from'] = strings.salary_to_k(matches[0], salary)
                args['expect_annual_salary_to']   = strings.salary_to_k(matches[1], salary)

            args['expect_salary_from'] = '%.2f' % (args['expect_annual_salary_from']/12)
            args['expect_salary_to']   = '%.2f' % (args['expect_annual_salary_to']/12)
        elif '个月' in salary and (matches := re.findall(r'(\d+.*)万（(\d+)元/月\s*\*\s*(\d+)个月）', salary, re.I | re.S)):
        # 年薪 19.60万（14000元/月 * 14个月）猎聘邮件
            if len(matches) == 1:
                args['expect_annual_salary_from'] = strings.salary_to_k(matches[0][0], 'W')
                args['expect_annual_salary_to']   = strings.salary_to_k(matches[0][0], 'W')
                args['expect_salary_from']        = strings.salary_to_k(matches[0][1])
                args['expect_salary_to']          = strings.salary_to_k(matches[0][1])
                args['expect_salary_month']        = matches[0][2]
        elif '薪' in salary and (matches := re.findall(r'(\d+\.\d+)万-(\d+\.\d+)万（(\d+)K/月-(\d+)K/月\*(\d+)薪）', salary, re.I | re.S)):
        # 年薪 13.20万-15.60万（11K/月-13K/月*12薪）猎聘通
            if len(matches) == 1:
                args['expect_annual_salary_from'] = strings.salary_to_k(matches[0][0], 'W')
                args['expect_annual_salary_to']   = strings.salary_to_k(matches[0][1], 'W')
                args['expect_salary_from']        = strings.salary_to_k(matches[0][2], 'K')
                args['expect_salary_to']          = strings.salary_to_k(matches[0][3], 'K')
                args['expect_salary_month']       = matches[0][4]

        elif matches := re.findall(r'(\d+\.*\d+)', salary, re.I | re.S):
            if len(matches) == 1:
                args['expect_salary_from'] = strings.salary_to_k(matches[0], salary)
                args['expect_salary_to']   = strings.salary_to_k(matches[0], salary)
            elif len(matches) == 2:
                args['expect_salary_from'] = strings.salary_to_k(matches[0], salary)
                args['expect_salary_to']   = strings.salary_to_k(matches[1], salary)

    return args


def handle_phone(args="", *extra):
    """
    match the phone number.
    """
    matches = re.search(r'(\d+)', args)
    if matches:
        return matches.group(0)
    else:
        return ""


def handle_email(args="", *extra):
    """
    match the email.
    """
    matches = re.search(r'(\S*@\S*)', args)
    if matches:
        return matches.group(0)
    else:
        return ""


# 公司类型
def handle_corp_type(args="", *extra):
    matches = re.search(r'(外资\(欧美\)|外资\(非欧美\)|合资|国企|民营公司|民营|上市公司|创业公司|外企代表处|政府机关|事业单位|非营利机构)', args)
    if matches:
        return matches.group(0)
    else:
        return ""


# 公司规模
def handle_corp_scale(args="", *extra):
    matches = re.search(r'(少于\d+|\d+[-,~]\d+|\d+.*?以上)', args)
    if matches:
        return matches.group(0)
    else:
        return ""
    

# 清洗技能
def wash_skill(args, *extra):
    parrten = r'(英语|日语|俄语|阿拉伯语|法语|德语|西班牙语|葡萄牙语|意大利语|韩语|朝鲜语|普通话|粤语|闽南语|上海话|其它)'
    if "name" not in args or not args['name']:
        return None
    elif "name" in args and re.findall(parrten, args['name'], re.S | re.I):
        return None
    else:
        return args


# 清洗语言
def wash_langue(args, *extra):
    parrten = r'(英语|日语|俄语|阿拉伯语|法语|德语|西班牙语|葡萄牙语|意大利语|韩语|朝鲜语|普通话|粤语|闽南语|上海话|其它)'
    if "name" in args and args['name']  and re.findall(parrten, args['name'], re.S | re.I):
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
            args['account'] = await http_curl(url=instance.config.get('rcp_service', None)['gsystem'], city=args['account_address'])
        if "address_detail" in args and args['address_detail']:
            args['address'] = await http_curl(url=instance.config.get('rcp_service', None)['gsystem'], city=args['address_detail'])
                
        
        args['account_district'] = args['account'] # 灵活用工使用
        args['address_district'] = args['address'] # 灵活用工使用

    return args


# 处理期望城市
async def handle_except_citys(args, *extra):
    if not isinstance(args, dict):
        return args
    else:
        # 籍贯所在地的市级ID
        args['expect_city_ids'] = ""

        import json
        if "expect_city_names" in args and args['expect_city_names']:
            citys = args['expect_city_names'].split(',')
            city_sets = []
            for _city in citys:
                gsys = await http_curl(url=instance.config.get('rcp_service', None)['gsystem'], city=_city)
                _tmp = max(gsys.split(','))
                city_sets.append(_tmp)

            args['expect_city_ids'] = strings.trim(','.join(city_sets))
        
    return args


async def handle_citys(args, *extra):
    """
        城市ID化
    """
    if not args:
        return ""

    import json
    citys = args.split(',')
    city_sets = []
    for _city in citys:
        gsys = await http_curl(url=instance.config.get('rcp_service', None)['gsystem'], city=_city)
        _tmp = max(gsys.split(','))
        city_sets.append(_tmp)

    args = strings.trim(','.join(city_sets))
        
    return args


global_citys = {}
# Gsystme 城市 ID 化
async def http_curl(**kwargs):
    if "city" not in kwargs or not kwargs['city']:
        return ""

    if "url" not in kwargs or not kwargs['url']:
        return ""

    if kwargs['city'] in global_citys:
        return global_citys[kwargs['city']]

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
            global_citys[kwargs['city']] = result
    except HTTPError as e:
        # HTTPError is raised for non-200 responses; the response
        # can be found in e.response.
        route.logger.warn("request gsystem HTTPError: " + str(e))
    except Exception as e:
        # Other errors are possible, such as IOError.
        route.logger.warn("request gsystem Exception: " + str(e))
    finally :
        http_client.close()

    return result


# 抓取头像（注：抓取头像会）
async def fetch_head(args:str="", *extra) -> str:
    if not args:
        return ""

    from tornado.httpclient import HTTPRequest,HTTPError
    from tornado.curl_httpclient import AsyncHTTPClient
    import pycurl,base64
    
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    http_client = AsyncHTTPClient()
    http_request = HTTPRequest(
        url=args,
        method='GET',
        headers={
            "Accept-Ranges": "bytes",
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "image/jpeg",
        },
        proxy_host='http://http-pro.abuyun.com',
        proxy_port=9010,
        proxy_username='HWZ4K0025R7161XP',
        proxy_password='373904A5540BC8BA',
    )

    result = ""
    try:
        response = await AsyncHTTPClient().fetch(http_request)
        result = base64.encodebytes(response.body).decode()
    except HTTPError as e:
        # HTTPError is raised for non-200 responses; the response
        # can be found in e.response.
        route.logger.warn("fetch_head HTTPError: " + str(e))
    except Exception as e:
        # Other errors are possible, such as IOError.
        route.logger.warn("fetch_head Exception: " + str(e))
    finally :
        http_client.close()

    return result
