#! /usr/bin/python3.8
# -*- coding:utf-8 -*-
# pylint: disable=W0223
import types

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
from functools import partial

from lib import route
from config import constant
from lib import loader
from lib import log
from utils import xmltodict
from utils import strings


class MainHandler(tornado.web.RequestHandler):
    """
        定义处理类型
    """

    def set_default_headers(self) -> None:
        tornado.log.logging.info("---set_default_headers---:设置header")

    @staticmethod
    def initialize():
        tornado.log.logging.info("---initialize---:初始化")

    def prepare(self):
        tornado.log.logging.info("---prepare---：准备工作")

        ip = self.request.headers.get("X-Real-Ip", self.request.remote_ip)
        ip = self.request.headers.get("X-Forwarded-For", ip)
        ip = ip.split(',')[0].strip()
        self.request.remote_ip = ip
        self.json_args = {}  # initialize args

        # 允许跨域请求
        if req_origin := self.request.headers.get('Origin'):
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
        if "application/json" in self.request.headers.get('Content-Type', ''):
            try:
                self.json_args = json.loads(self.request.body)
            except TypeError:
                self.send_error(400)

        # xml格式请求
        elif 'application/xml' in self.request.headers.get('Content-Type', ''):
            try:
                self.json_args = xmltodict.parse(self.request.body)
            except TypeError:
                self.send_error(501)

        # 普通参数请求
        elif self.request.arguments:
            self.json_args = dict((k, v[-1]) for k, v in self.request.arguments.items())

        tornado.log.logging.warning("---Params---：%s" % json.dumps(self.json_args))

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

            trace_back_info = kwargs.get('exc_info')[2]
            for filename, line_num, func_name, source in traceback.extract_tb(trace_back_info, -1):
                tornado.log.access_log.warning("%-23s:%s '%s' in %s()", filename, line_num, source, func_name)

        self.set_status(200)
        self.write({'status_code': status_code, 'reason': reason})

    def on_finish(self):
        tornado.log.logging.info("---on_finish---：结束，释放资源")


def log_request(handler):
    """
        记录请求日志
    """
    if handler.get_status() < 400:
        log_method = tornado.log.access_log.info
    elif handler.get_status() < 500:
        log_method = tornado.log.access_log.warning
    else:
        log_method = tornado.log.access_log.error

    request = handler.request
    log_method('"%s %s" %d %s %.6f', request.method, request.uri, handler.get_status(), request.remote_ip,
               request.request_time())


def signal_handler(server: tornado.httpserver, signum: int, frame_type: types.FrameType) -> None:
    """
        系统捕获信号处理
    """

    print("Received Signal: %s at frame: %s" % (signum, dir(frame_type)))

    import os
    logger = log.Log().getLog()
    logger.warning('Current processes id:%s, Parent processes id:%s, Caught signal: %s', os.getpid(), os.getppid(),
                   signum)

    if signum not in [signal.SIGINT, signal.SIGTERM]:
        print(os.wait())
        logger.warning('Not expected signal')

    ###########################
    ##  做一些处理，保证入库等  ##
    ###########################

    io_loop = tornado.ioloop.IOLoop.instance()

    def stop_loop(service: tornado.httpserver, deadline: float):
        now = time.time()

        # 获取当前事件循环中还没有结束的任务（任务不是正在运行的任务和已经完成的任务，既pending状态的任务）
        # Future对象有以下状态：Pending,Running,Done,Cancelled
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task() and not t.done()]
        if now < deadline and len(tasks) > 0:
            logger.warning(f'Awaiting {len(tasks)} pending tasks: {tasks}')
            io_loop.add_timeout(now + 1, stop_loop, service, deadline)
            return

        pending_connection = len(service._connections)
        if now < deadline and pending_connection > 0:
            logger.warning(f'Waiting on {pending_connection} connections to complete.')
            io_loop.add_timeout(now + 1, stop_loop, service, deadline)
        else:
            logger.warning('Stopping http server, and stop receive the http request.')
            service.stop()
            logger.warning(f'Continuing with {pending_connection} connections open.')
            logger.warning('Stopping IOLoop')
            io_loop.stop()
            logger.warning('Shutdown complete.')

    def shutdown():
        TORNADO_SHUTDOWN_WAIT = 1
        logger.warning(f'Will shutdown in {TORNADO_SHUTDOWN_WAIT} seconds ...')
        try:
            stop_loop(server, time.time() + TORNADO_SHUTDOWN_WAIT)
        except BaseException as e:
            logger.warning(f'Error trying to shutdown Tornado: {str(e)}')

    io_loop.add_callback_from_signal(shutdown)

    os.kill(os.getppid(), signal.SIGKILL)


def run():
    env = "development"
    port = 8880
    thread_num = 2

    usage = u'''使用参数启动:
                usage: python main.py [-p] [-e] [-tn]

                -e [environment] ******使用环境,可选[development,testing,production]
                                       ,默认:development
                -p [port]        ******启动端口,默认:8880
                -tn[thread_num]  ******启用进行数，默认:2
                -h [help]        ******帮助信息
            '''
    try:
        opts, _ = getopt.getopt(sys.argv[1:], "h:e:tn:p", [
            "help",
            "env=",
            "port=="
            "thread_num=",
        ])
    except ValueError:
        print(usage)
        sys.exit(0)

    for opt, value in opts:
        if opt == '-e' or opt == '--env':
            if value in ['production', 'testing']:
                env = value

        elif opt == '-p' or opt == '--port':
            if not value.isdigit():
                print("{} 端口格式错误".format(value))
                sys.exit(0)
            port = int(value)
            if strings.net_used(port):
                print("{} 端口已被占用".format(value))
                sys.exit(0)

        elif opt == '-tn' or opt == '--thread_num':
            if not value.isdigit():
                print("{} 格式错误".format(value))
                sys.exit(0)
            thread_num = int(value)

        elif opt == '-h' or opt == '--help':
            print(usage)
            sys.exit(0)

    os.chdir(os.path.join(os.path.dirname(__file__), '..'))
    env_config = os.path.join(constant.CONF_PATH, env, 'config.json')
    print("no configuration found!,will use [%s] instead" % env_config)

    # 加载配置文件
    env_config | loader.load_func(loader.instance.load) | loader.load_func(loader.instance.setup)

    app = tornado.web.Application([
        (r"^(/[^\.|]*)(?!\.\w+)$", MainHandler),  # 路由
    ], log_function=log_request)  # 创建一个应用对象
    server = tornado.httpserver.HTTPServer(app)

    # 绑定的端口
    server.bind(port)

    # 开启的进程数量
    server.start(thread_num)

    # 信号注册
    # signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, partial(signal_handler, server))

    tornado.ioloop.IOLoop.current().start()  # 启动web程序，开始监听端口的连接


# 系统执行入口
if __name__ == "__main__":
    run()
