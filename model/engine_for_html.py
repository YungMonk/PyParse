#!/usr/bin/python3.8
# -*- coding: utf-8 -*-

import re
import array
import os,sys
import json
import hashlib

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from tornado.web import HTTPError

from lib import helper, path, route
from lxml import etree
from config import static_param


class hEngine(object):

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
        logger = route.logger
        self.__cache = route.lfu_cache


    async def dispatch(self):
        # 58同城的简历内容需要字体解码
        if self.__site == 12:
            self.__text = helper.font_decrypt(self.__text) 

        etreehtml = etree.HTML(self.__text)

        # result = etreehtml.xpath("string(//table[@class='infr'])")
        # print(result)

        # 读取内存缓存
        tmp_key = hashlib.new('md5', self.__text.encode("utf-8")).hexdigest()
        # if p_result := self.__cache.get(tmp_key):
        #     return p_result

        # 读取配置信息
        tplConf = json.loads(self.readFile("config.json"))
        config_tpl = await self.parse(tplConf, etreehtml)

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
        for key, maps in config_tpl.items():
            if recursive(maps):
                configKey = key
        if configKey == '':
            raise HTTPError(500003, "渠道的简历格式发生了变化")

        templateName = tplConf[configKey]['fname']

        templateContent = json.loads(self.readFile(templateName))
        cv = await self.parse(templateContent, etreehtml)

        p_result = json.dumps(cv, ensure_ascii=False)

        # 写入内存缓存
        self.__cache.set(tmp_key, p_result, ttl=30)

        return p_result


    # 内容解析
    async def parse(self, maps, etreehtml):
        tmp = {}
        for key, value in maps.items():

            # 用来调试
            # if key == 'skill':
            #     print(etreehtml)

            # 处理默认值
            if 'value' in value:
                tmp[key] = value['value']
                continue

            # 处理规则为空的情况
            if 'rules' not in value or len(value['rules']) == 0:
                value['rules'] = '/'

            rules = value['rules']

            # 分割规则
            arr = rules.split('|')

            # 选项是否是字符串
            if isinstance(etreehtml, str):
                expath = etreehtml
            else:
                expath = etreehtml.xpath(helper.placeholder(arr[0]))
            
            # 子项处理前对html文本数据进行处理
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

        filepath = os.path.join(path._TEMPLATE, siteName, static_param.parserType[
            self.__type], 'html', filename)

        logger.warn("loading file: %s" % filepath)

        if not os.path.exists(filepath):
            if filename == 'config.json':
                raise HTTPError(500001, "渠道不支持")
            else:
                raise HTTPError(500002, "解析模板未找到")

        with open(filepath, 'r') as fopen:
            content = fopen.read()
            fopen.close()

            if not fopen.closed:
                logger.fatal("file is not closed: %s" % filepath)

        return content


    def xpath_to_html(self, xpath_list:list):
        return etree.tostring(xpath_list, encoding="utf-8", pretty_print=True, method="html").decode()
