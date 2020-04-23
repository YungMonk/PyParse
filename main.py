#! /usr/bin/python
# -*- coding:utf-8 -*-

import tornado.ioloop
import tornado.web
import tornado.log

import getopt
import os
import json
import sys

from lib import route
from lib import path
from lib import configer
from utils import xmltodict


# 定义处理类型
class MainHandler(tornado.web.RequestHandler):

    def prepare(self):
        ip = self.request.headers.get("X-Real-Ip", self.request.remote_ip)
        ip = self.request.headers.get("X-Forwarded-For", ip)
        ip = ip.split(',')[0].strip()
        self.request.remote_ip = ip
        self.json_args = {}  # initialize args

        # 允许跨域请求
        if (req_origin := self.request.headers.get('Origin')):
            self.set_header('Access-Control-Allow-Origin', req_origin)
            self.set_header("Access-Control-Allow-Credentials", "true")
            self.set_header("Allow", "GET, HEAD, POST")

            if self.request.method == "OPTIONS":
                self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
                self.set_header("Access-Control-Allow-Headers", "Accept, Cache-Control, Content-Type")
                self.finish()
                return
            else:
                self.set_header("Cache-Control", "no-cache")


        # json格式请求
        if self.request.headers.get('Content-Type', '').find("application/json") >= 0:
            try:
                self.json_args = json.loads(self.request.body)
            except Exception:
                self.send_error(400)


        # xml格式请求
        elif self.request.headers.get('Content-Type', '').find('application/xml') >= 0:
            try:
                self.json_args = xmltodict.parse(self.request.body)
            except Exception:
                self.send_error(501)


        # 普通参数请求
        elif self.request.arguments:
            self.json_args = dict((k, v[-1]) for k, v in self.request.arguments.items())

        
    # 添加一个处理get请求方式的方法
    @tornado.gen.coroutine
    def get(self, path):
        route.router.get(path, self)
        
    @tornado.gen.coroutine
    def post(self, path):
        route.router.post(path, self)
        
    @tornado.gen.coroutine
    def put(self, path):
        route.router.put(path, self)
        
    @tornado.gen.coroutine
    def delete(self, path):
        route.router.delete(path, self)

    @tornado.gen.coroutine
    def options(self, path):
        route.router.options(path, self)


def log_request(handler) :
    if handler.get_status() < 400:
        log_method = tornado.log.access_log.info
    elif handler.get_status() < 500:
        log_method = tornado.log.access_log.warning
    else:
        log_method = tornado.log.access_log.error

    request = handler.request
    log_method('"%s %s" %d %s %.6f',request.method, request.uri, handler.get_status(), request.remote_ip, request.request_time() )
         

if __name__ == "__main__":

    os.chdir(os.path.join(os.path.dirname(__file__), '..'))

    env_config = None

    opts, argvs = getopt.getopt(sys.argv[1:], "c:p:h")
    for opt, value in opts:
        if opt == '-c':
            env_config = value
            path._CONF_PATH = os.path.dirname(os.path.abspath(value))
        elif opt == '-p':
            port = int(value)
        elif opt == '-h':
            print (
                u'''使用参数启动:
                        usage: [-p|-c]
                        -p [prot] ******启动端口,默认端口:%d
                        -c <file> ******加载配置文件
                ''' % port
            )
            sys.exit(0)

    if not env_config:
        env_config = os.path.join(path._CONF_PATH, 'dev.json')
        print("no configuration found!,will use [%s] instead" % env_config)

    conf = configer.ConfigParserFromFile()
    env_config | configer.E(conf.parseall) | configer.E(configer.conf.setup)

    app = tornado.web.Application([
        (r"^(/[^\.|]*)(?!\.\w+)$", MainHandler),  # 路由
    ], log_function=log_request)  # 创建一个应用对象

    app.listen(8888)    # 设置端口

    tornado.ioloop.IOLoop.current().start()  # 启动web程序，开始监听端口的连接

    # tornado.ioloop.IOLoop.current().close()
