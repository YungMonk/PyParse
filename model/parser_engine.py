#!/usr/bin/python3.8
# -*- coding: utf-8 -*-

import re
import array
import os,sys
import json

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from tornado.web import HTTPError

from lib import helper, path, log
from lxml import etree
from config import static_param


class ParserEngine(object):

    __site = 0
    __type = 0  # 1:简历 2:职位
    __text = ""
    __conf = ""

    __parse_result = {}

    typeArr = array.array('i', [1, 2])


    def __init__(self, **args):
        self.__site = args['site_id']
        self.__text = args['body']
        self.__type = args['type']

        global logger
        logger = log.Log().getLog()


    async def dispatch(self):
        etreehtml = etree.HTML(self.__text)

        # result = etreehtml.xpath("string(//table[@class='infr'])")
        # print(result)

        # 读取配置信息
        tplConf = json.loads(self.readFile("config.json"))
        configParser = await self.parse(tplConf, etreehtml)

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

        # 选择模板文件
        configKey = ''
        for key, maps in configParser.items():
            if recursive(maps):
                configKey = key
        if configKey == '':
            raise HTTPError(80012, "not found the template!!!")

        templateName = tplConf[configKey]['fname']

        templateContent = json.loads(self.readFile(templateName))
        cv = await self.parse(templateContent, etreehtml)

        return json.dumps(cv, ensure_ascii=False)


    # 内容解析
    async def parse(self, maps, etreehtml):
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
            expath = etreehtml.xpath(helper.placeholder(arr[0]))
            if len(expath) > 0  and len(arr[1:]) > 1 and arr[1] == 'call_prev':
                _html = ""
                for _etree in expath:
                    _html = _html + self.xpath_to_html(_etree)
                expath = await helper.optimize(_html, arr[1:])

            if 'child' in value and isinstance(value['child'], dict) and len(value['child']):
                # 有子项
                if 'lists' in value and value['lists'] and len(expath):
                    # 子项是列表,父项有值
                    t = []
                    for sign in expath:
                        tmp_child = await self.parse(value['child'], sign)
                        if 'application_rules' in value and value['application_rules']:
                            tmp_child = await helper.optimize(tmp_child, value['application_rules'].split('|'))

                        if tmp_child :
                            t.append(tmp_child)
                        
                    tmp[key] = t
                elif 'lists' in value and value['lists'] and not expath:
                    # 子项是列表,父项没有值
                    tmp[key] = []
                else:
                    # 子项不是列表
                    if len(expath):
                        # 父项有值
                        tmp[key] = await self.parse(value['child'], expath[0])
                    else:
                        # 父项没有值
                        tmp[key] = await self.parse(value['child'], etreehtml)

                    if 'application_rules' in value and value['application_rules']:
                        tmp[key] = await helper.optimize(tmp[key], value['application_rules'].split('|'))

            else:
                # 没有子项
                if len(expath) == 0:
                    tmp[key] = ''
                elif isinstance(expath, str):
                    tmp[key] = expath
                elif isinstance(expath[0], str):
                    tmp[key] = expath[0]
                else:
                    tmp[key] = expath[0].text if expath[0].text else ""

                # 子项处理后对html文本数据进行处理
                if tmp[key] and len(arr) > 1:
                    tmp[key] = await helper.optimize(tmp[key], arr[1:])

        return tmp


    def readFile(self, filename):
        content = ""
        siteName = static_param.channelMap[self.__site]

        filepath = path._TEMPLATE + '/' + siteName + '/' + static_param.parserType[
            self.__type] + '/' + filename
        if os.path.exists(filepath) is False:
            print(filepath + " is not found")

        with open(filepath, 'r') as fopen:
            content = fopen.read()
            fopen.close()

            if fopen.closed == False:
                print("file is not closed")

        return content


    def xpath_to_html(self, xpath_list:list):
        return etree.tostring(xpath_list, encoding="utf-8", pretty_print=True, method="html").decode()

        
        

if __name__ == '__main__':
    print(os.getcwd())
    filename = os.getcwd() + '/test/data/51job/1.1.html'
    with open(filename, 'r') as f:
        fileContext = f.read()
        f.close()

    try :

        obj = ParserEngine(site_id=2, body=fileContext, type=1)
        obj.dispatch()
    except Exception as exp :
        print(exp)
    
