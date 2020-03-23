#!/usr/bin/python
# -*- coding: utf-8 -*-

import array, os, json
from lxml import etree
from django.utils.html import strip_tags
from config.static_param import channelMap, parserType
from lib.helper import optimize


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

            expath = etreehtml.xpath(value['rules'])
            if 'child' in value and isinstance(value['child'], dict) and len(
                    value['child']):
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
            
            if 'cback' in value:
                    tmp[key] = optimize(tmp[key], value['cback'])
            # print(tmp[key], key)

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


filename = os.getcwd() + '/test/carjob/1.html'
with open(filename, 'r') as f:
    fileContext = f.read()
    f.close()
    # print(fileContext)

    obj = ParserEngine(51, fileContext, 1)
    obj.dispatch()