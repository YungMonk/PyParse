#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import array
import os
import json
from lxml import etree
from config.static_param import channelMap, parserType
from lib.helper import optimize, preg_match


class ParserEngine(object):

    __site = 0
    __type = 0  # 1:简历 2:职位
    __text = ""
    __conf = ""

    __parse_result = {}

    typeArr = array.array('i', [1, 2])

    def __init__(self, site, text, type):
        if site == 0 or site == '':
            print("site is empty")
        self.__site = site
        if text == "":
            print("text is empty")
        self.__text = text
        if self.typeArr.count(type) == 0:
            print("type is empty")
        self.__type = type

    def dispatch(self):
        etreehtml = etree.HTML(self.__text)

        # 读取配置信息
        tplConf = json.loads(self.readFile("config.json"))
        configParser = self.parse(tplConf, etreehtml)

        # 递归遍历字典
        def recursive(dictOlist):
            res = True
            for ele in dictOlist.values():
                if isinstance(ele, dict):
                    tmp = recursive(ele)
                    if tmp is not True:
                        res = tmp
                else:
                    if len(ele):
                        pass
                    else:
                        res = False
            return res

        # 选择模板文件 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
        configKey = ''
        for key, maps in configParser.items():
            if recursive(maps):
                configKey = key

        templateName = tplConf[configKey]['fname']

        templateContent = json.loads(self.readFile(templateName))
        cv = self.parse(templateContent, etreehtml)

        print(cv)

    def placeholder(self, str=''):
        return str.replace('@或@', '|').replace('逗号', ',').replace('左中括号', '[').replace(
            '右中括号', ']').replace('右括号', '(').replace('左括号', ')').replace('\\n', '\n')

    def filter(self, str):
        matches = []
        if preg_match(str, pattern=r'/(.*?)\[(.*)\],(\d+)/'):
            pass

    def parse(self, maps, etreehtml):
        tmp = {}
        for key, value in maps.items():

            # 处理默认值
            if 'value' in value and value['value']:
                tmp[key] = value['value']
                continue

            # 处理规则为空的情况
            if 'rules' not in value or len(value['rules']) == 0:
                value['rules'] = '/'

            rules = value['rules']

            # 分割规则
            arr = rules.split('|')

            # 子项处理前对html文本数据进行处理
            expath = etreehtml.xpath(self.placeholder(arr[0]))
            if expath and 'pfunc' in value:
                # print(expath)
                htmltext = etree.tostring(
                    expath[0], encoding="utf-8", pretty_print=True, method="html").decode()
                htmltext = optimize(htmltext, value['pfunc'])
                # print(htmltext)

            if 'child' in value and isinstance(value['child'], dict) and len(value['child']):
                # 有子项
                if 'lists' in value and value['lists'] and len(expath):
                    t = []
                    for sign in expath:
                        t.append(self.parse(value['child'], sign))
                    tmp[key] = t
                else:
                    if len(expath):
                        # 本级规则不为空
                        tmp[key] = self.parse(value['child'], expath[0])
                    else:
                        # 本级规则为空
                        tmp[key] = self.parse(value['child'], etreehtml)
            else:
                # 没有子项
                if len(expath) == 0:
                    tmp[key] = ''
                else:
                    tmp[key] = expath[0].text

            # 子项处理后对html文本数据进行处理
            arr.pop(0)
            if len(arr):
                print(arr)
                tmp[key] = optimize(tmp[key], arr)

        return tmp

    def readFile(self, filename):
        content = ""
        siteName = channelMap[self.__site]

        filepath = os.getcwd() + '/template/' + siteName + '/' + parserType[
            self.__type] + '/' + filename
        if os.path.exists(filepath) is False:
            print(filepath + " is not found")

        with open(filepath, 'r') as fopen:
            content = fopen.read()
            fopen.close()

            if fopen.closed == False:
                print("file is not closed")

        return content


# filename = os.getcwd() + '/test/carjob/1.html'
# with open(filename, 'r') as f:
#     fileContext = f.read()
#     f.close()
#     # print(fileContext)

#     obj = ParserEngine(51, fileContext, 1)
#     obj.dispatch()
strs = "起始位置2019-01-02/2020-09-01/2020-10-11"
pattern = re.compile(r'(\d{4}.*?\d{1,2}).*?(\d{1,2})')
print(pattern.findall(strs))
print(pattern.search(strs).group())
