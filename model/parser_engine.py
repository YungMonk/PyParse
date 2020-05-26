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

from lib import helper, path, error, log
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

        # 选择模板文件
        configKey = ''
        for key, maps in configParser.items():
            if recursive(maps):
                configKey = key
        if configKey == '':
            logger.warn("not found the template!!!", exc_info=True)
            raise HTTPError(400, log_message="not found the template!!!")

        templateName = tplConf[configKey]['fname']

        templateContent = json.loads(self.readFile(templateName))
        cv = self.parse(templateContent, etreehtml)

        # print(json.dumps(cv, ensure_ascii=False))
        return json.dumps(cv, ensure_ascii=False)


    # 内容解析
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
            expath = etreehtml.xpath(helper.placeholder(arr[0]))

            if len(arr) > 1 and arr[1] == 'call_prev':
                htmltext = etree.tostring(
                    expath[0], encoding="utf-8", pretty_print=True, method="html").decode()
                expath = helper.optimize(htmltext, arr[1:])

            if 'child' in value and isinstance(value['child'], dict) and len(value['child']):
                # 有子项
                if 'lists' in value and value['lists'] and len(expath):
                    t = []
                    for sign in expath:
                        tmp_child = self.parse(value['child'], sign)

                        if 'application_rules' in value and value['application_rules']:
                            tmp_child = helper.optimize(
                                tmp_child, value['application_rules'].split('|'))

                        t.append(tmp_child)
                    tmp[key] = t
                else:
                    if len(expath):
                        # 本级规则不为空
                        tmp[key] = self.parse(value['child'], expath[0])
                    else:
                        # 本级规则为空
                        tmp[key] = self.parse(value['child'], etreehtml)

                    if 'application_rules' in value and value['application_rules']:
                        tmp[key] = helper.optimize(
                            tmp[key], value['application_rules'].split('|'))

            else:
                # 没有子项
                if len(expath) == 0:
                    tmp[key] = ''
                elif isinstance(expath[0], str):
                    tmp[key] = expath[0]
                else:
                    tmp[key] = expath[0].text

                # 子项处理后对html文本数据进行处理
                if tmp[key] and len(arr) > 1:
                    tmp[key] = helper.optimize(tmp[key], arr[1:])
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

    # @staticmethod
    # def engine(cls, ctx, rule) :

        
        

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
    
