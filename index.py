#! /usr/bin/python
# -*- coding:utf-8 -*-

import tornado.ioloop
import tornado.web
import tornado.log
import tornado.httpserver

import asyncio
import getopt
import os
import json
import sys
import time
import signal
import traceback

from lib import route
from lib import path
from lib import configer
from lib import log
from utils import xmltodict


# 定义处理类型
class MainHandler(tornado.web.RequestHandler):
    
    def set_default_headers(self):
        tornado.log.logging.info("---set_default_headers---:设置header")
    
    def initialize(self):
        tornado.log.logging.info("---initialize---:初始化")

    def prepare(self):
        tornado.log.logging.info("---prepare---：准备工作")

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
    async def get(self, path):
        await route.router.get(path, self)
        
    async def post(self, path):
        await route.router.post(path, self)

    async def put(self, path):
        await route.router.put(path, self)
        
    async def delete(self, path):
        await route.router.delete(path, self)

    async def options(self, path):
        await route.router.options(path, self)

    def write_error(self, status_code, **kwargs):
        tornado.log.logging.info("---write_error---：处理错误")
        
        # 获取send_error中的reason，默认值是 unknown
        reason = kwargs.get('reason', 'unknown')

        # 获取HTTPError中的log_message作为reason
        if 'exc_info' in kwargs:
            exception = kwargs['exc_info'][1]
            if isinstance(exception, tornado.web.HTTPError) and exception.log_message:
                reason = exception.log_message

            tracebackinfo = kwargs.get('exc_info')[2]
            for filename, linenum, funcname, source in traceback.extract_tb(tracebackinfo, -1):
                tornado.log.access_log.warning("%-23s:%s '%s' in %s()", filename, linenum, source, funcname) 

        self.set_status(200)
        self.write({'status_code': status_code, 'reason': reason})

    def on_finish(self):
        tornado.log.logging.info("---on_finish---：结束，释放资源")

# 记录请示日志
def log_request(handler) :
    if handler.get_status() < 400:
        log_method = tornado.log.access_log.info
    elif handler.get_status() < 500:
        log_method = tornado.log.access_log.warning
    else:
        log_method = tornado.log.access_log.error

    request = handler.request
    log_method('"%s %s" %d %s %.6f',request.method, request.uri, handler.get_status(), request.remote_ip, request.request_time())
         

# 系统捕获信号处理
def sig_handler(sig, frame):
    logger = log.Log().getLog()
    logger.warning('Caught signal: %s', sig)
    tornado.ioloop.IOLoop.current().add_callback(shutdown)


# 处理系统关闭信号
def shutdown():
    io_loop = tornado.ioloop.IOLoop.current()
    
    ##########################
    ##  做一些处理，保证入库等  ##
    ##########################

    deadline = time.time() + 5

    def stop_loop():
        now = time.time()
        if now < deadline and (io_loop._callbacks or io_loop._timeouts):
            io_loop.add_timeout(now + 1, stop_loop)
        else:
            io_loop.stop() # 处理完现有的 callback后，结束ioloop循环
    
    stop_loop()


# 系统执行入口
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

    # app.listen(8880)    # 设置端口

    server = tornado.httpserver.HTTPServer(app)

    server.bind(8880)

    server.start(2)  

    # 信号注册
    # signal.signal(signal.SIGTERM, sig_handler)
    # signal.signal(signal.SIGINT, sig_handler)

    tornado.ioloop.IOLoop.current().start()  # 启动web程序，开始监听端口的连接