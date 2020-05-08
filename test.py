#! /usr/bin/python
# -*- coding:utf-8 -*-

import time
import signal
import http
import urllib.request

import tornado.ioloop
import tornado.web

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
    response = urllib.request.urlopen("https://www.runoob.com/mongodb/php7-mongdb-tutorial.html")
    filestrs = response.read().decode('utf8')
    return filestrs

if __name__ == "__main__":

    app = tornado.web.Application([
        (r"/", MainHandler),  # 路由
        (r"/test", TestHandler),  # 路由
    ])  # 创建一个应用对象

    app.listen(8880)    # 设置端口

    io_loop = tornado.ioloop.IOLoop.current()
    io_loop.start()  # 启动web程序，开始监听端口的连接
