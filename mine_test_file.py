#!/usr/bin/python3.8
# -*- coding: utf-8 -*-

import tornado.web
import tornado.ioloop
import urllib.request
import http
import signal
import time
import json
import cgi
import datetime
import socketserver
import urllib
import io
import os

from http import server
from model.parser_engine import ParserEngine


class http_request_handler(server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_error(415, 'Only post is supported')

    def do_POST(self):
        path = str(self.path)  # 获取请求的url
        if path == '/parse':
            length = int(self.headers['content-length'])  # 获取除头部后的请求参数的长度
            datas = self.rfile.read(length)  # 获取请求参数数据，请求数据为json字符串
            rjson = json.loads(datas.decode())
            print(rjson, type(rjson))

            filename = os.getcwd() + '/test/carjob/1.html'
            with open(filename, 'r') as f:
                fileContext = f.read()
                f.close()
                obj = ParserEngine(51, fileContext, 1)
                result = obj.dispatch()

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(result.encode())

        else:
            self.send_error(404, "Not Found")


# 定义处理类型
class MainHandler(tornado.web.RequestHandler):

    @tornado.gen.coroutine
    def post(self):
        ret = yield c()
        raise tornado.gen.Return(ret)
        # self.write("写入")

        # self.finish("Hello World")


class TestHandler(tornado.web.RequestHandler):

    async def get(self):
        filestrs = await c()
        self.write("Fetched " + str(len(filestrs)) + " entries ")


async def c():
    response = urllib.request.urlopen(
        "https://www.runoob.com/mongodb/php7-mongdb-tutorial.html")
    filestrs = response.read().decode('utf8')
    return filestrs


if __name__ == '__main__':
    # 原生 HTTP 服务
    # try:
    #     with socketserver.TCPServer(("", 8000), http_request_handler) as httpd:
    #         httpd.serve_forever()
    # except KeyboardInterrupt:
    #     print('^c received,shutting down the web server!')

    # Tornado 框架 HTTP 服务
    app = tornado.web.Application([
        (r"/", MainHandler),  # 路由
        (r"/test", TestHandler),  # 路由
    ])  # 创建一个应用对象

    app.listen(8880)    # 设置端口

    io_loop = tornado.ioloop.IOLoop.current()
    io_loop.start()  # 启动web程序，开始监听端口的连接
