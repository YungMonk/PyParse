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
        elif (tmp := re.search(r'(.*)\[(.*)\],(-*\d+)', func)):
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
            if call_info[0] in ["handle_address_city", "handle_except_citys", "handle_position_city", "fetch_head"]:
                args = await func(args)
            else :
                args = func(args)

    return args


def placeholder(str=''):
    '''
        占位符还原
    '''
    return str.replace('@或@', '|').replace('逗号', ',').replace('左中括号', '[').replace('右中括号', ']').replace('左括号', '(').replace('右括号', ')').replace('\\n', '\n')


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


def strip_tags(args="", *extra):
    '''
        去除html文本中的所有标签
    '''
    return strings.strip_tags(args)


def explode(args="", *extra):
    '''
        字符串分割
    '''
    return args.split(extra[0] if len(extra) else " ")


def implode(args="", *extra):
    '''
        字符串拼接
    '''
    if len(extra) and extra[0] :
        return extra[0].join(args)
    else:
        return ",".join(args)


def array_column(args: dict, *extra) -> list:
    '''
        获取字典中感兴趣的列
    '''
    if len(extra) and extra[0] :
        return [array.get(extra[0], '') for array in args]


def preg_match(args="", *extra):
    '''
        正则使用
    '''
    if len(extra) and extra[0] and (matches := re.search(extra[0], args, re.S | re.I)):
        return matches.groups()


def preg_match_all(args="", *extra):
    '''
        正则全匹配
    '''
    if len(extra) and extra[0] and (matches := re.findall(extra[0], args, re.S | re.I)):
        return matches


def preg_replace(args="", *extra):
    '''
        正则替换
    '''
    if len(extra) and extra[0]:
        return re.sub(extra[0], extra[1] if len(extra) > 1 else "", args)
    else:
        return args


def json_encode(args="", *extra):
    '''
        josn序列化
    '''
    import json
    return json.dumps(args, ensure_ascii=False)


def k2k(args="", *extra):
    '''
        单位（千）转换
    '''
    return strings.salary_to_k(args)


def w2k(args="", *extra):
    '''
        单位（万）转换
    '''
    return strings.salary_to_k(args, 'W')


def handle_regualr(args="", *extra):
    '''
        正则分割
    '''
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


def handle_xpath(args="", *extra):
    '''
        xpath处理
    '''
    return etree.HTML(args).xpath(placeholder(extra[0]))

def handle_birth(args="", *extra):
    '''
        拼接出生日期
    '''
    birth = ""
    if 'birth_year' in args and args['birth_year']:
        birth = args['birth_year'] + '年'
        if 'birth_month' in args and args['birth_month']:
            birth = birth + args['birth_month'] + '月'
            if 'birth_day' in args and args['birth_day']:
                birth = birth + args['birth_day'] + '日'
        args['birth'] = birth

    return args

def handle_birthday(args="", *extra):
    '''
        匹配出生日
    '''
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


def handle_age(args="", *extra):
    '''
        匹配年龄
    '''
    string = ""
    if (matchObj := re.search(r'(\d+)\s*岁', args)):
        string = matchObj.group(1)
    elif (matchObj := re.search(r'(\d{4})\s*年*', args)):
        birt_year = matchObj.group(1)
        string = time.localtime().tm_year - strings.atoi(birt_year) + 1
    elif (matchObj := re.search(r'(\d{4}).*?\d{1,2}', args)):
        birt_year = matchObj.group(1)
        string = time.localtime().tm_year - strings.atoi(birt_year) + 1
    return string


def handle_gender(args="", *extra):
    '''
        匹配性别
    '''
    sexs = {'男': 'M', '女': 'F', 'male': 'M', 'female': 'F', 'women': 'F', 'men': 'M','woman': 'F', 'man': 'M'}
    if (isMatch := re.search(r'(男|女|male|female|women|men|woman|man)', args)):
        return sexs[isMatch.group(1)]
    elif (isMatch := re.search(r'(\d)', args)):
        return sexs[isMatch.group(1)]


def handle_degree(args="", *extra):
    '''
        匹配学历
    '''
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


def handle_langue(args="", *extra):
    '''
        语言匹配
    '''
    if (isMatch := re.search(r'(英语|日语|俄语|阿拉伯语|法语|德语|西班牙语|葡萄牙语|意大利语|韩语/朝鲜语|普通话|粤语|闽南语|上海话|其它)', args)):
        return isMatch.group(1)
    else:
        return ""


def handle_sofar(args="", *extra):
    '''
        是否最近
    '''
    if 'start_time' in args and 'end_time' in args and args['end_time'] == '':
        args['so_far'] = 'Y'
    else:
        args['so_far'] = 'N'
    return args


def handle_marital(args="", *extra):
    '''
        婚姻状态
    '''
    marital = {'已婚': 'Y', '未婚': 'N', '保密':'U', 'single': 'N', 'married': 'Y', 'unmarried': 'N'}
    if (isMatch := re.search(r'(已婚|未婚|single|married|unmarried)', args)):
        return marital[isMatch.group(1)]
    else:
        return "U"


def handle_experience_by_years(args:str="", *extra) -> str:
    '''
        通过参加工作年获取工作经验
    '''
    if not args or not args.isdigit():
        return ""

    year_start = args[:4]
    return time.localtime().tm_year - strings.atoi(year_start) + 1


def handle_basic_experience(args="", *extra):
    '''
        工作经验
    '''
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
    elif (isMatch := re.search(r'([\u4e00-\u9fa5]+)年', experience)):
        # 八年
        args["working_seniority_to"] = cn2dig(isMatch.group(1))
        args["working_seniority_from"] = args["working_seniority_to"]
        args["work_experience"] = args["working_seniority_to"]

    return args


def handle_current_status(args="", *extra):
    '''
        当前状态
    '''
    status = 0
    if re.search(r'在岗|在职|机会', args, re.S|re.I):
        status = 3
    elif re.search(r'离职|找工作|求职中', args, re.S|re.I):
        status = 1

    return status

def handle_political(args="", *extra) -> str:
    '''
        政治背景
    '''
    parrten = r'(中共党员|共产党员|预备党员|团员|民主党派|无党派人士|无党派民主人士|群众|其他)'
    if matches := re.findall(parrten, args, re.S | re.I):
        return matches[0]
    else:
        return ""


def handle_update(args="", *extra) -> str:
    '''
        简历更新时间
    '''
    return time.strftime("%Y-%m-%d", time.localtime(strings.str_to_time(args)))


def handle_time(args="", *extra):
    '''
        处理时间
    '''
    if matches := re.findall(r'(\d{4}.*?\d{1,2}.{1})', re.sub(r'(\d{4}).*?(\d{1,2})', '\\1年\\2月', args)):
        return matches[0]
    elif matches := re.findall(r'(\d{4}年)', args):
        return matches[0]
    else:
        return ""


def handle_interval(args="", *extra):
    '''
        处理时间间隔
    '''
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


def handle_education(args="", *extra):
    '''
        通过毕业时间和学位，获取学历时间
    '''
    args['start_time'] = ""
    args['end_time'] = ""
    args['so_far'] = "N"

    isMatch = re.findall(r'(\d{4}).*?(\d{1,2})', args['time'])
    edu_time = '{}年{}月'.format(isMatch[0][0],isMatch[0][1])
    years = 4 if args['degree'] == 1 else 3
    if 'is_grad' in args and args['is_grad']:
        args['end_time'] = edu_time
        args['start_time'] = '{}年{}月'.format(strings.atoi(isMatch[0][0]) - years, "09")
    if 'is_grad' in args and not args['is_grad']:
        args['end_time'] = '{}年{}月'.format(strings.atoi(isMatch[0][0]) + years, "07")
        args['start_time'] = edu_time

    args = handle_sofar(args, *extra)

    args.pop('is_grad','')
    args.pop('time','')
    return args


def handle_basic_salary(args="", *extra):
    '''
        处理基本薪资
    '''
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


def handle_expect_salary(args="", *extra):
    '''
        处理期望薪资
    '''
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

        elif 'k' in salary and (matches := re.findall(r'(\d+)', salary, re.I | re.S)):
            # 拉钩的薪资5k-10k
            if len(matches) == 1:
                args['expect_salary_from'] = strings.salary_to_k(matches[0], salary)
                args['expect_salary_to']   = strings.salary_to_k(matches[0], salary)
            elif len(matches) == 2:
                args['expect_salary_from'] = strings.salary_to_k(matches[0], salary)
                args['expect_salary_to']   = strings.salary_to_k(matches[1], salary)
        elif matches := re.findall(r'(\d+\.*\d+)', salary, re.I | re.S):
            # 匹配薪资float  12.0
            if len(matches) == 1:
                args['expect_salary_from'] = strings.salary_to_k(matches[0], salary)
                args['expect_salary_to']   = strings.salary_to_k(matches[0], salary)
            elif len(matches) == 2:
                args['expect_salary_from'] = strings.salary_to_k(matches[0], salary)
                args['expect_salary_to']   = strings.salary_to_k(matches[1], salary)

    return args


def handle_phone(args="", *extra):
    '''
        匹配手机号
    '''
    matches = re.search(r'(\d+)', args)
    if matches:
        return matches.group(0)
    else:
        return ""


def handle_email(args="", *extra):
    '''
        匹配邮箱号
    '''
    matches = re.search(r'(\S*@\S*)', args)
    if matches:
        return matches.group(0)
    else:
        return ""


def handle_corp_name_merge(args="", *extra):
    '''
        公司名称合并
    '''
    args['corporation_name'] = "{}{}".format(args['corporation_name_1'],args['corporation_name_2'])
    args.pop('corporation_name_1','')
    args.pop('corporation_name_2', '')
    return args


def handle_contact_merge(args="", *extra):
    '''
        联系方式合并
    '''
    phone = ''
    email = ''
    delete_key = []
    if isinstance(args,(dict,)):
        for k,v in args.items():
            if 'phone_num' in k:
                delete_key.append(k)
                if match_phone := re.search(r'([1][3578]\d{9})', v):
                    phone = match_phone.group(1)
            if 'email_num' in k:
                delete_key.append(k)
                if match_email := re.search(r'(^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+$)',v):
                    email = match_email.group(1)
    args['phone'] = phone
    args['email'] = email
    for key in delete_key:
        args.pop(key, '')

    return args


def handle_corp_type(args="", *extra):
    '''
        公司类型
    '''
    matches = re.search(r'(外资\(欧美\)|外资\(非欧美\)|合资|国企|私营\/民营|民营公司|民营|上市公司|创业公司|外企代表处|政府机关|国有企业|事业单位|非营利机构)', args)
    if matches:
        return matches.group(0)
    else:
        return ""


def handle_corp_scale(args="", *extra):
    '''
        公司规模
    '''
    matches = re.search(r'(少于\d+|\d+\s*[-,~]\s*\d+|\d+人以上)', args, re.S|re.I)
    if matches:
        return matches.group(0)
    else:
        return ""


def handle_position_language(args="", *extra):
    '''
        职位语言要求
    '''
    level = {'一般': 1, '良好': 2, '熟练': 3, '精通': 4}
    lans = {'英语' : 1, '日语' : 2, '韩语' : 3, '法语' : 4, '西班牙语' : 5, '德语' : 6,'俄语' : 7, '阿拉伯语' : 8, '葡萄牙语' : 9, '意大利语' : 10}
    
    args["languages"] = []
    args["language"] = ""

    if 'language' not in args or not args['language']:
        return args

    if not extra:
        split_tag_1 = '\n'
        split_tag_2 = ':'
    elif len(extra) == 1:
        split_tag_1 = '\n'
        split_tag_2 = extra[0]
    elif len(extra) == 2:
        split_tag_1 = extra[0]
        split_tag_2 = extra[1]

    languages = args.split(split_tag_1)
    for lan in languages:
        array = lan.split(split_tag_2)
        tmp = {"id": "","name":"","level":""}
        if len(array) == 2:
            tmp["id"] = lans[strings.trim(array[0])] if strings.trim(array[0]) in lans else ""
            tmp["name"] = array[0]
            tmp["level"] = level[strings.trim(array[1])] if strings.trim(array[1]) in level else ""
        else :
            tmp["id"] = lans[strings.trim(array[0])] if strings.trim(array[0]) in lans else ""
            tmp["name"] = array[0]
            tmp["level"] = "" 

        if not tmp["id"]:
            continue
        args["languages"].append(tmp)

    if not args["languages"]:
        args["language"] = ""
    else:
        args["language"] = json_encode(args["languages"])

    return args


def handle_position_number(args="", *extra):
    '''
        匹配招聘人数
    '''
    args['number'] = ''
    args['number_up'] = 'N'

    if 'number' not in args:
        return args

    if '以上' in args['number']:
        args['number_up'] = 'Y'
        
    isMatch = re.search(r'(\d+\s*)(?=人)', args['number'])
    if isMatch:
        args['number'] = isMatch[0]

    return args


def handle_position_degree(args="", *extra):
    '''
        匹配学历
    '''
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
    if 'degree_name' not in args:
        args['degree_name'] = '不限'
        args['degree'] = 99
        args['degree_above'] = 'N'
        return args
    
    if '以上' in args['degree_name']:
        args['degree_above'] = 'Y'
    else:
        args['degree_above'] = 'N'
    
    if (isMatch := re.search(r'(初中|高中|中专|中技|专科|大专|本科|硕士|博士|MBA)', args['degree_name'])):
        args['degree_name'] = isMatch.group(1)
        args['degree'] = degrees[isMatch.group(1)]
    else:
        args['degree_name'] = '不限'
        args['degree'] = 99
    
    return args

def handle_position_salary(args="", *extra):
    '''
        处理期望薪资
    '''
    args['salary_begin'] = 0
    args['salary_end'] = 500

    if "salary" in args:
        salary = args['salary']
        if '年' in salary and (matches := re.findall(r'(\d+\.*\d*)', salary, re.I | re.S)):
        # 年薪 10万，10.5万，10-15万，10万-15万
            if len(matches) == 1:
                salary_begin = strings.salary_to_k(matches[0], salary)
                salary_end   = strings.salary_to_k(matches[0], salary)
            elif len(matches) == 2:
                salary_begin = strings.salary_to_k(matches[0], salary)
                salary_end   = strings.salary_to_k(matches[1], salary)
            args['salary_begin'] = '%.2f' % (float(salary_begin) / 12)
            args['salary_end']   = '%.2f' % (float(salary_end) / 12)
        elif '个月' in salary and (matches := re.findall(r'(\d+.*)万（(\d+)元/月\s*\*\s*(\d+)个月）', salary, re.I | re.S)):
        # 年薪 19.60万（14000元/月 * 14个月）猎聘邮件
            if len(matches) == 1:
                args['salary_begin']        = strings.salary_to_k(matches[0][1])
                args['salary_end']          = strings.salary_to_k(matches[0][1])
        elif '薪' in salary and (matches := re.findall(r'(\d+\.\d+)万-(\d+\.\d+)万（(\d+)K/月-(\d+)K/月\*(\d+)薪）', salary, re.I | re.S)):
        # 年薪 13.20万-15.60万（11K/月-13K/月*12薪）猎聘通
            if len(matches) == 1:
                args['salary_begin']        = strings.salary_to_k(matches[0][2], 'K')
                args['salary_end']          = strings.salary_to_k(matches[0][3], 'K')
        elif matches := re.findall(r'(\d+\.*\d*)', salary, re.I | re.S):
            # 匹配薪资float  12.0
            if len(matches) == 1:
                args['salary_begin'] = strings.salary_to_k(matches[0], salary)
                args['salary_end']   = strings.salary_to_k(matches[0], salary)
            elif len(matches) == 2:
                args['salary_begin'] = strings.salary_to_k(matches[0], salary)
                args['salary_end']   = strings.salary_to_k(matches[1], salary)

    return args


def handle_position_experience(args="", *extra):
    '''
        职位工作经验
    '''
    args['experience_begin'] = 0
    args['experience_end'] = 0
    args['experience_above'] = "N"

    if "experience" not in args or not args["experience"]:
        return args
    
    experience = args["experience"]
    if re.search(r'不限|无要求', experience):
        # 不限
        args['experience_begin'] = 0
        args['experience_end'] = 0
    elif re.search(r'应届毕业生|无经验', experience):
        # 应届毕业生,无经验
        args['experience_begin'] = 0
        args['experience_end'] = -1
    elif re.search(r'在读', experience):
        # 在读学生,在读生
        args['experience_begin'] = 0
        args['experience_end'] = -2
    elif (isMatch := re.search(r'(\d{1,2})年以下(工作经验|经验)*', experience)):
        # 10年以下工作经验，8年以下经验
        args["experience_end"] = isMatch.group(1)
    elif (isMatch := re.search(r'(\d{1,2})(\s|\.0)*年以上(工作经验|经验)*', experience)):
        # 10以上工作经验，10.0年以上工作经验，8年以上经验
        args["experience_begin"] = isMatch.group(1)
        args['experience_above'] = "Y"
    elif (isMatch := re.search(r'(\d{1,2})-(\d{1,2})年(工作经验|经验)*', experience)):
        # 8-10年工作经验，8-10年经验
        args["experience_begin"] = isMatch.group(1)
        args["experience_end"]   = isMatch.group(2)
    elif (isMatch := re.search(r'(\d{1,2})年(工作经验|经验)', experience)):
        # 8年工作经验
        args["experience_begin"] = isMatch.group(1)
        args["experience_end"]   = args["experience_begin"]
    elif (isMatch := re.search(r'(\d{1,2})years', experience)):
        # 10years
        args["experience_begin"] = isMatch.group(1)
        args["experience_end"]   = args["experience_begin"]
    elif (isMatch := re.search(r'(\d{1,2})\s*年(?!\d)', experience)):
        # 10 年，10年
        args["experience_begin"] = isMatch.group(1)
        args["experience_end"]   = args["experience_begin"]
    elif (isMatch := re.search(r'([\u4e00-\u9fa5]+)年以上', experience)):
        # 十年以上工作经验
        args["experience_begin"] = cn2dig(isMatch.group(1))
        args['experience_above'] = "Y"
    elif (isMatch := re.search(r'([\u4e00-\u9fa5]+)年', experience)):
        # 八年
        args["experience_begin"] = cn2dig(isMatch.group(1))
        args["experience_end"]   = args["experience_begin"]

    return args


def handle_position_delete(args="", *extra):
    '''
        职位已删除
    '''
    if 'is_deleted' not in args:
        args['is_deleted'] = 'N'
    elif re.search(r'停止|暂停|过期|expired|company_gq|结束|error-404|火星|删除|404|301|暂时', args['is_deleted']):
        args['is_deleted'] = 'Y'
    else:
        args['is_deleted'] = 'N'

    return args


def handle_position_publish(args="", *extra):
    '''
        职位发布时间
    '''
    import datetime
    from dateutil.relativedelta import relativedelta
    if 'created' not in args:
        args['created'] = ''
    elif isMatch := re.findall(r'(\d{4})[-,/,年](\d{1,2})[-,/,月](\d{1,2})', args['created']):
        args['created'] = "-".join(isMatch[0])
    elif isMatch := re.findall(r'(\d{4})[-,/,年](\d{1,2})', args['created']):
        args['created'] = "-".join(isMatch[0])
    elif isMatch := re.findall(r'(\d{1,2})[-,/,月](\d{1,2})', args['created']):
        args['created'] = "{}-{}".format(time.localtime().tm_year, "-".join(isMatch[0]))
    elif re.findall(r'刚刚|分钟前|小时前|今天', args['created']):
        args['created'] = str(datetime.date.today())
    elif re.findall(r'昨天', args['created']):
        args['created'] = str(datetime.date.today() - relativedelta(days=1))
    elif re.findall(r'前天', args['created']):
        args['created'] = str(datetime.date.today() - relativedelta(days=2))
    elif isMatch := re.findall(r'(\d{1,2})个*月前', args['created']):
        m = strings.atoi(isMatch[0])
        args['created'] = str(datetime.date.today() - relativedelta(month=m))
    elif isMatch := re.findall(r'(\d{1,2})天前', args['created']):
        d = strings.atoi(isMatch[0])
        args['created'] = str(datetime.date.today() - relativedelta(days=d))
    else:
        args['created'] = ''

    return args


def wash_education(args="", *extra):
    '''
        清洗教育经历
    '''
    if isinstance(args, (dict,)) and args['other_information'] == '培训':
        args.pop('name', '')
        args.pop('corporation_name', '')
        args.pop('school_name', '')
    return args


def wash_training(args="", *extra):
    '''
        清洗培训经历
    '''
    if isinstance(args, (dict,)) and args['other_information'] != '培训':
        args.pop('name', '')
        args.pop('corporation_name', '')
        args.pop('school_name', '')
    return args


def wash_skill(args, *extra):
    '''
        清洗技能
    '''
    parrten = r'(英语|日语|俄语|阿拉伯语|法语|德语|西班牙语|葡萄牙语|意大利语|韩语|朝鲜语|普通话|粤语|闽南语|上海话|其它)'
    if "name" not in args or not args['name']:
        return None
    elif "name" in args and re.findall(parrten, args['name'], re.S | re.I):
        return None
    else:
        return args


def wash_langue(args, *extra):
    '''
        清洗语言
    '''
    parrten = r'(英语|日语|俄语|阿拉伯语|法语|德语|西班牙语|葡萄牙语|意大利语|韩语|朝鲜语|普通话|粤语|闽南语|上海话|其它|English|Chinese)'
    if "name" in args and args['name']  and re.findall(parrten, args['name'], re.S | re.I):
        return args
    else:
        return None


def wash_name_null(args, *extra):
    '''
        清洗名称为空的
    '''
    if "name" in args and args['name']:
        return args
    elif "corporation_name" in args and args['corporation_name']:
        return args
    elif "school_name" in args and args['school_name']:
        return args
    else:
        return None


#################################################################
######################### 异步方法调用  ###########################
#################################################################
async def handle_position_city(args, *extra) -> dict:
    '''
        处理职位城市
    '''
    if not isinstance(args, dict):
        return args
    else:
        args['city_ids'] = {}
        args['workplace'] = {}

        import json
        if "city" in args and args['city']:
            gsys = await http_gsystem(url=instance.config.get('rcp_service', None)['gsystem'], city=args['city'])
            city = max(gsys.split(','))

            args['city_ids'] = {city: args['city']}
            args['workplace'] = {'id': city, 'name': args['city']}
            
            args.pop('city','')

    return args

async def handle_address_city(args, *extra) -> dict:
    '''
        户籍，现居住地相关（单个城市）
    '''
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
            args['account'] = await http_gsystem(url=instance.config.get('rcp_service', None)['gsystem'], city=args['account_address'])
        if "address_detail" in args and args['address_detail']:
            args['address'] = await http_gsystem(url=instance.config.get('rcp_service', None)['gsystem'], city=args['address_detail'])


        args['account_district'] = args['account'] # 灵活用工使用
        args['address_district'] = args['address'] # 灵活用工使用

    return args


async def handle_except_citys(args, *extra):
    '''
        处理期望城市（多个城市）
    '''
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
                gsys = await http_gsystem(url=instance.config.get('rcp_service', None)['gsystem'], city=_city)
                _tmp = max(gsys.split(','))
                city_sets.append(_tmp)

            args['expect_city_ids'] = strings.trim(','.join(city_sets))

    return args


global_citys = {}
async def http_gsystem(**kwargs):
    '''
        请求第三方服务 gsystem
    '''
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


async def fetch_head(args:str="", *extra) -> str:
    '''
        抓取头像（注：抓取头像会）
    '''
    if not args:
        return ""

    if re.search(r'man|male|female|user_female|img/photo\.png|img\.58cdn\.com\.cn/m58', args):
        return ""

    # 拉钩默认头像
    if "myresume/default_headpic.png" in args or 'image/pc/default' in args:
        return ""

    # jobcn默认头像
    if 'photoBlankV3_men2' in args or 'photoBlankV3_women2' in args:
        return ""

    # 补全链接
    if re.search(r'^//', args):
        args = 'http:' + args

    if not re.search(r'^http', args):
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
        result = base64.b64encode(response.body).decode()
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

#################################################################
######################### 其它过滤方法  ###########################
#################################################################
def font_decrypt(args: str = "", *extra) -> str:
    '''
        58同城字体解密
    '''
    from fontTools.ttLib import TTFont
    import io
    import os
    import base64
    import hashlib
    from lib import path

    font_dict = {
        "uniE0A3": "硕", "uniE103": "A", "uniE108": "士", "uniE17A": "女", "uniE29E": "M",
        "uniE2D9": "专", "uniE32C": "8", "uniE413": "科", "uniE470": "验", "uniE53C": "6",
        "uniE5D0": "赵", "uniE713": "1",  "uniE724": "高", "uniE73B": "大", "uniE869": "E",
        "uniE9B3": "下", "uniE9EA": "校", "uniEA12": "届", "uniEA43": "7", "uniEAED": "男",
        "uniEB29": "5", "uniEB71": "3", "uniEBBD": "2", "uniEBD6": "经", "uniED6C": "中",
        "uniEE32": "9", "uniEE47": "技", "uniEE8F": "周", "uniEF06": "本", "uniEFA9": "0",
        "uniEFCA": "博", "uniF02F": "4", "uniF031": "生", "uniF16F": "杨", "uniF19B": "王",
        "uniF38D": "陈", "uniF3E6": "张", "uniF484": "刘", "uniF48A": "以", "uniF696": "应",
        "uniF729": "吴", "uniF77D": "黄", "uniF84C": "无", "uniF874": "B", "uniF885": "李",
    }

    matches = re.search(r'\(data:application/font-woff;charset=utf-8;base64,(.*?)\)', args)
    if matches:
        font_chart = matches.group(1)
        font_temp = base64.b64decode(font_chart)

        # 当前的字体是否已经存在，不存在保存
        key_temp = hashlib.new('md5', font_chart.encode("utf-8")).hexdigest()
        new_font_name = os.path.join(path._SCRIPT_FONT, key_temp+".woff")
        if not os.path.exists(new_font_name):
            with open(new_font_name, 'wb') as f:
                f.write(font_temp)
                f.close()

        # 得到基准字体的编码
        font_base = TTFont(os.path.join(path._SCRIPT_FONT, "base.woff"))
        font_base_order = font_base.getGlyphOrder()[1:]

        # 得到当前字体的编码
        font_curr = TTFont(io.BytesIO(font_temp))
        font_curr_order = font_curr.getGlyphOrder()[1:]

        result = {}
        for curr_i in font_curr_order:
            if curr_i == 'x':
                continue

            curr_ttglyph = font_curr['glyf'][curr_i]
            for base_i in font_base_order:
                if base_i == 'x':
                    continue

                base_ttglyph = font_base['glyf'][base_i]

                # 字体的组成部分个数是否相同
                if curr_ttglyph.numberOfContours != base_ttglyph.numberOfContours:
                    continue

                base_xOffset = min([x[0] for x in base_ttglyph.coordinates])
                base_yOffset = min([x[1] for x in base_ttglyph.coordinates])

                curr_xOffset = min([x[0] for x in curr_ttglyph.coordinates])
                curr_yOffset = min([x[1] for x in curr_ttglyph.coordinates])

                re_base_coordinates = []
                for base_contours in base_ttglyph.coordinates:
                    re_base_coordinates.append(
                        str(base_contours[0] - base_xOffset) + '-' +
                        str(base_contours[1] - base_yOffset)
                    )


                re_curr_coordinates = []
                for curr_contours in curr_ttglyph.coordinates:
                    re_curr_coordinates.append(
                        str(curr_contours[0] - curr_xOffset) + '-' +
                        str(curr_contours[1] - curr_yOffset)
                    )

                instan = list(set(re_base_coordinates) & set(re_curr_coordinates))

                if not len(instan) or len(instan) / len(re_base_coordinates) < 0.5 :
                    continue

                result[curr_i] = font_dict[base_i]

        result = {re.sub('uni(.*)','&#x\\1;', key):value for key, value in result.items()}

        for key,val in result.items():
            args = args.replace(key,val)

    return args


def get_info_by_id(args: str = "", *extra) -> str:
    '''
        通过id获取值
    '''
    if not args or len(extra) < 1 or not extra[0]:
        return ""

    pkg = __import__('config.static_zhaopin', fromlist=['static_zhaopin'])
    if not hasattr(pkg, extra[0]):
        return ""

    tmp_set = getattr(pkg, extra[0])
    tmp_map = {val[0]: {"parent_id": val[1], "name": val[2], } for val in tmp_set}

    result = ""
    temp = args.split(',')
    for tmp_id in temp:
        if tmp_id not in tmp_map:
            continue
        result = result + ',' + tmp_map[tmp_id]['name']

    return strings.trim(result, ',')
