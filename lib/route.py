#!/usr/bin/python3.8
# -*- coding: utf-8 -*-

import inspect
import logging
import re
import os
import sys

import tornado.web
from cacheout import LFUCache

from lib import loader
from lib import log
from config import constant

# 加载缓存
lfu_cache: LFUCache

logger: logging.Logger


@loader.config.register(level=2)
def set_up():
    """ erase all nodes
        this function maybe called for hot deployment
    """

    # 加载日志
    global logger
    logger = log.Log().getLog()

    global lfu_cache
    lfu_cache = LFUCache(maxsize=256)

    files_list = os.listdir(constant.CONTROLLER_PATH)
    files_list = set(['controller.' + x[:x.rfind('.')] for x in files_list if x.endswith('.py')])
    list(map(__import__, files_list))

    router.pre_check()


class router(object):
    """dispatcher and decorator"""

    _GET = 0x001
    _PUT = 0x004
    _POST = 0x002
    _DELETE = 0x008
    _OPTIONS = 0x010
    mapper = []
    mapper_sentry = {}
    last_sentry = {}

    @classmethod
    def check_redefined_node(cls, sentry, url_exp, method):
        if not sentry:
            return None

        if sentry['eUrl'] == url_exp and sentry['method'] & method:
            return sentry
        else:
            return router.check_redefined_node(sentry['next'], url_exp, method)

    @classmethod
    def lookup_suitable_node(cls, prev, sentry, url, method, assert_wrong_method=False):
        """
            循环加载所有路由
        """
        if not sentry:

            if assert_wrong_method:
                raise tornado.web.HTTPError(405)

            raise tornado.web.HTTPError(404)

        wrong = assert_wrong_method

        if matches := sentry['eUrl'].match(url):

            if sentry['method'] & method:  # hit!

                if prev:
                    prev['next'] = sentry['next']
                    sentry['next'] = router.mapper_sentry
                    router.mapper_sentry = sentry

                return sentry, matches

            else:
                wrong = True

        return router.lookup_suitable_node(sentry, sentry['next'], url, method, wrong)

    @classmethod
    def pre_check(cls):
        """
            路由检查
        """

        check_mapper_list = []

        for item in set(router.mapper):

            if router.mapper.count(item) > 1:
                check_mapper_list.append(item)

        if check_mapper_list:

            for check_child in check_mapper_list:
                logger.fatal('Definition conflict : FUNCTION[%s]', check_child[0])

            sys.exit(1)

    @classmethod
    def route(cls, **deco):
        """
            用以注册路由的装饰器
        """

        def foo(func):
            url = deco.get('url') or '/'
            eUrl = re.compile('^' + url + '$', re.IGNORECASE)
            method = deco.get('method') or router._GET

            if router.check_redefined_node(router.mapper_sentry, eUrl, method):
                logger.fatal('Definition conflict : URL[%s]', url)
                sys.exit(1)
            else:
                mapper_node = {
                    'eUrl': eUrl,
                    'method': method,
                    'callName': func.__name__,
                    'className': inspect.stack()[1][3],
                    'moduleName': func.__module__,
                    'next': {},
                }

                router.mapper.append(
                    '.'.join([mapper_node['moduleName'], mapper_node['className'], mapper_node['callName']]))

                # Yes, I used linked list here
                # Any better way to contain urls?
                # Disadvantage: have to visit the urls list from head to end to
                # determined 404

                if router.mapper_sentry:
                    router.last_sentry['next'] = mapper_node
                    router.last_sentry = router.last_sentry['next']
                else:
                    router.mapper_sentry = mapper_node
                    router.last_sentry = router.mapper_sentry

            return func

        return foo

    @classmethod
    async def emit(cls, path, request_handler, method_flag):
        """
            路由分发
        """
        mapper_node, m = router.lookup_suitable_node(None, router.mapper_sentry, path, method_flag)

        if mapper_node and m:
            params = (request_handler,)

            for items in m.groups():
                params += (items,)

            callName = mapper_node['callName']
            className = mapper_node['className']
            moduleName = mapper_node['moduleName']
            clazz = getattr(__import__(moduleName, fromlist=moduleName[moduleName.rfind('.') + 1:]), className)

            obj = None
            try:
                obj = clazz()
            except ModuleNotFoundError:
                logger.exception("error occurred when creating instance of %s" % className)
                pass

            call = getattr(obj, callName)
            ret = await call(*params)
            request_handler.finish(ret)

    @classmethod
    async def get(cls, path, request_handler):
        await router.emit(path, request_handler, router._GET)

    @classmethod
    async def post(cls, path, request_handler):
        await router.emit(path, request_handler, router._POST)

    @classmethod
    async def put(cls, path, request_handler):
        await router.emit(path, request_handler, router._PUT)

    @classmethod
    async def delete(cls, path, request_handler):
        await router.emit(path, request_handler, router._DELETE)

    @classmethod
    async def options(cls, path, request_handler):
        await router.emit(path, request_handler, router._OPTIONS)
