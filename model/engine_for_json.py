#!/usr/bin/python3.8
# -*- coding: utf-8 -*-

from config.static_param import channelMap, parserType
from lib.route import lfu_cache, logger
from lib import path, helper
from tornado.web import HTTPError

from utils import strings

import hashlib
import json
import os
import sys

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)


class jEngine(object):

    def __init__(self, **kawge):

        self.text = kawge['body']
        self.type = kawge['type']
        self.site = kawge['site_id']

    async def dispatch(self):
        """解析json格式简历内容"""

        try:
            ctx = json.loads(self.text)
        except Exception as e:
            raise HTTPError(100002, "format wrong:%s" % e)

        # 读取内存缓存
        tmp_key = hashlib.new('md5', self.text.encode("utf-8")).hexdigest()
        # if p_result := lfu_cache.get(tmp_key):
        #     return p_result

        # 配置文件读取
        tpl_conf = json.loads(self.get_config_ctx('config.json'))
        res_list = await self.parse(tpl_conf, ctx)

        def recursive(dictOlist):
            # 递归遍历字典
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
        for key, maps in res_list.items():
            if recursive(maps):
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
                    if isinstance(tmp_res, str):
                        result[key] = await helper.optimize(tmp_res, tmp_arr[1:])
                    else:
                        result[key] = json.dumps(tmp_res, ensure_ascii=False)
                else:
                    result[key] = ""
                continue

            """有子项"""
            if 'rules' in val and val['rules']:
                # 过滤规则不为空
                tmp_arr = val['rules'].split('|')
                tmp_res = strings.get_val_by_keys(tmp_arr[0], ctx)
                if 'list' in val and val['list'] and isinstance(tmp_res, list):
                    # 子项返回值要求是列表
                    tmp = []
                    for _val in tmp_res:
                        _tmp = await self.parse(val['child'], tmp_res)
                        tmp.append(_tmp)
                    result[key] = tmp
                else:
                    # 子项返回值要求是字典
                    result[key] = await self.parse(val['child'], tmp_res)
            else:
                # 过滤规则为空
                result[key] = await self.parse(val['child'], ctx)

        return result

    def get_config_ctx(self, file: str = ""):
        """获取文件内容"""
        file_name = os.path.join(
            path._TEMPLATE,
            channelMap[self.site],
            parserType[self.type],
            'json',
            file,
        )
        logger.warn("loading file: %s" % file_name)

        if not os.path.exists(file_name):
            if file_name == 'config.json':
                raise HTTPError(500001, "渠道不支持")
            else:
                raise HTTPError(500002, "解析模板未找到")

        with open(file_name, 'r') as fopen:
            ctx = fopen.read()
            fopen.close()

            if not fopen.closed:
                logger.fatal("file is not closed: %s" % file_name)

        return ctx
