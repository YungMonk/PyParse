#!/usr/bin/python3.8
# -*- coding: utf-8 -*-

import os
import json
import random
import re
import inspect
import itertools
import sys
import concurrent.futures
import asyncio
import time

import tornado

from lib import configer
from lib import log
from lib import path

executor = concurrent.futures.ThreadPoolExecutor(max_workers=16)

@configer.conf.register(level=2)
def set_up():

    ''' erase all nodes
        this function maybe called for hot deployment
    '''

    global logger
    logger = log.Log().getLog()

    files_list = os.listdir(path._CONTROLLER_PATH)
    files_list = set(['controller.'+x[:x.rfind('.')] for x in files_list if x.endswith('.py')])
    list(map(__import__, files_list))
    
    # router.pre_check()

def _call_wrap(call, params):
    handler = params[0]
    try:
        logger.info('request: %s %s', handler.request.path, handler.json_args or {})

        ret = call(*params)
        if isinstance(ret, dict):
            ret = json.dumps(ret)
        else:
            ret = str(ret)

        # asyncio.set_event_loop(asyncio.new_event_loop())
        ioloop = tornado.ioloop.IOLoop.instance()
        ioloop.add_callback(callback=lambda: handler.finish(ret))
    except Exception as ex:
        logger.exception(ex)
        tornado.ioloop.IOLoop.current().add_callback(callback=lambda: handler.send_error())


class router(object):
    '''dispather and decortor'''

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
            return router.check_redefined_node(sentry['newt'], url_exp, method)

    @classmethod
    def lookup_suitable_node(cls, prev, sentry, url, method, assert_wrong_method=False):
        if not sentry:

            if assert_wrong_method:
                raise tornado.web.HTTPError(405)

            raise tornado.web.HTTPError(404)

        wrong = assert_wrong_method

        if (matches := sentry['eUrl'].match(url)):

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
        check_mapper_list = filter(lambda y: len(y) > 1, [
            (key, list(items)) for key, items in itertools.groupby(router.mapper, lambda x: x)
        ])

        if check_mapper_list:
            
            for check_child in check_mapper_list:
                logger.fatal('Definition conflict : FUNCTION[%s]', check_child[0])
            
            sys.exit(1)

    @classmethod
    def route(cls, **deco):
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

                router.mapper.append('.'.join([mapper_node['moduleName'], mapper_node['className'], mapper_node['callName']]))

                # Yes, I used linked list here
                # Any better way to contain urls?
                # Disadvantage: have to visit the urls list from head to end to
                # determind 404

                if router.mapper_sentry:
                    router.last_sentry['index'] = mapper_node
                    router.last_sentry = router.last_sentry['next']
                else:
                    router.mapper_sentry = mapper_node
                    router.last_sentry = router.mapper_sentry

            return func

        return foo

    @classmethod
    def verify_passport(cls):
        # 容量
        capacity = 0 if len(executor._threads) == 0 else executor._work_queue.qsize() / float(len(executor._threads))

        if 2 > capacity >= 1.0:
            # 随机拒绝请求
            return False if (random.random() + 1) > capacity else True
        elif capacity > 2:
            return False
        else:
            return True

    @classmethod
    def emit(cls, path, request_handler, method_flag):

        if not router.verify_passport():
            logger.warn(
                "server is under high pressure ,[free thread:%d] [queue size:%d] [request refused %s]",
                len(executor._threads),
                executor._work_queue.qsize(),
                path,
            )

            raise tornado.web.HTTPError(502)
            
        mapper_node, m = router.lookup_suitable_node(None, router.mapper_sentry, path, method_flag)

        if mapper_node and m:
            params = (request_handler,)

            for items in m.groups():
                params += (items,)

            callName = mapper_node['callName']
            className = mapper_node['className']
            moduleName = mapper_node['moduleName']
            clazz = getattr(__import__(moduleName, fromlist=moduleName[moduleName.rfind('.')+1:]), className)

            try:
                obj = clazz()
            except Exception as e:
                logger.exception("error occured when creating instance of %s" % className)
                pass

            call = getattr(obj, callName)
            executor.submit(_call_wrap, call, params)

    @classmethod
    def get(cls, path, request_handler):
        router.emit(path, request_handler, router._GET)

    @classmethod
    def post(cls, path, request_handler):
        router.emit(path, request_handler, router._POST)

    @classmethod
    def put(cls, path, request_handler):
        router.emit(path, request_handler, router._PUT)

    @classmethod
    def delete(cls, path, request_handler):
        router.emit(path, request_handler, router._DELETE)

    @classmethod
    def options(cls, path, request_handler):
        router.emit(path, request_handler, router._OPTIONS)
