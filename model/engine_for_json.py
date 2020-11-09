#!/usr/bin/python3.8
# -*- coding: utf-8 -*-

import hashlib
import json
import os
import sys

from tornado.web import HTTPError

from config import constant, static_param
from lib import helper
from lib.route import logger, lfu_cache
from utils import strings

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)


class jEngine(object):

    def __init__(self, **kawge):

        self.__site = kawge['site_id']
        self.__text = kawge['body']
        self.__type = kawge['type']

    async def dispatch(self):
        """解析json格式简历内容"""

        try:
            ctx = json.loads(self.__text)
        except Exception as e:
            raise HTTPError(100002, "format wrong:%s" % e)

        # 读取内存缓存
        tmp_key = hashlib.new('md5', self.__text.encode("utf-8")).hexdigest()
        # if p_result := lfu_cache.get(tmp_key):
        #     return p_result

        # 配置文件读取
        tpl_conf = json.loads(self.get_config_ctx('config.json'))
        config_tpl = await self.parse(tpl_conf, ctx)

        def recursive(dict_list):
            # 递归遍历字典
            res = True
            for ele in dict_list.values():
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
            if isinstance(maps, dict) and recursive(maps):
                configKey = key
        if configKey == '':
            raise HTTPError(500003, "渠道的简历格式发生了变化")

        templateName = tpl_conf[configKey]['fname']

        templateContent = json.loads(self.get_config_ctx(templateName))
        cv = await self.parse(templateContent, ctx)

        p_result = json.dumps(cv, ensure_ascii=False)

        # 写入内存缓存
        lfu_cache.set(tmp_key, p_result, ttl=30)

        return p_result

    async def parse(self, rule_map: dict, ctx: dict) -> dict:
        """解析主逻辑"""
        result = {}
        for key, val in rule_map.items():
            """有默认值"""
            if 'value' in val:
                result[key] = val['value']
                continue

            """没有子项或子项为空"""
            if 'child' not in val or not val['child']:
                if 'rules' in val and val['rules']:
                    tmp_arr = val['rules'].split('|')
                    tmp_res = strings.get_val_by_keys(tmp_arr[0], ctx)
                    if isinstance(tmp_res, int):
                        result[key] = await helper.optimize(str(tmp_res), tmp_arr[1:])
                    else:
                        result[key] = await helper.optimize(tmp_res, tmp_arr[1:])
                else:
                    result[key] = ""
                continue

            """有子项"""
            if 'rules' in val and val['rules']:
                # 过滤规则不为空
                tmp_arr = val['rules'].split('|')
                tmp_res = strings.get_val_by_keys(tmp_arr[0], ctx)
                if 'lists' in val and val['lists']:
                    tmp = []
                    if isinstance(tmp_res, list):
                        # 子项返回值要求是列表
                        for _val in tmp_res:
                            _tmp = await self.parse(val['child'], _val)

                            if 'application_rules' in val and val['application_rules']:
                                _tmp = await helper.optimize(_tmp, val['application_rules'].split('|'))

                            if not _tmp:
                                continue
                            
                            tmp.append(_tmp)
                    result[key] = tmp
                else:
                    # 子项返回值要求是字典
                    result[key] = await self.parse(val['child'], tmp_res)
                    if 'application_rules' in val and val['application_rules']:
                        result[key] = await helper.optimize(result[key], val['application_rules'].split('|'))
            else:
                # 过滤规则为空
                result[key] = await self.parse(val['child'], ctx)
                if 'application_rules' in val and val['application_rules']:
                    result[key] = await helper.optimize(result[key], val['application_rules'].split('|'))

            # result[key] = await helper.optimize(tmp_res, tmp_arr[1:])

        return result

    def get_config_ctx(self, filename: str = ""):
        """获取文件内容"""
        filepath = os.path.join(
            constant.TEMPLATE,
            static_param.channelMap[self.__site],
            self.__type,
            'json',
            filename,
        )
        logger.warning("loading file: %s" % filepath)

        if not os.path.exists(filepath):
            if filename == 'config.json':
                raise HTTPError(500001, "渠道不支持")
            else:
                raise HTTPError(500002, "解析模板未找到")

        with open(filepath, 'r') as fopen:
            ctx = fopen.read()
            fopen.close()

            if not fopen.closed:
                logger.fatal("file is not closed: %s" % filepath)

        return ctx
