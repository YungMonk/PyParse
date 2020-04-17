#! /usr/bin/python
# -*- coding:utf-8 -*-

import tornado.ioloop
import tornado.web

# 定义处理类型
class MainHandler(tornado.web.RequestHandler):

    # 添加一个处理get请求方式的方法
    def get(self):
        self.write("Hello, world")
    def post(self):
        self.write("Hello, world")


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler), # 路由
    ])


if __name__ == "__main__":

    app = make_app()    # 创建一个应用对象

    app.listen(8888)    # 设置端口

    tornado.ioloop.IOLoop.current().start() #启动web程序，开始监听端口的连接

    # tornado.ioloop.IOLoop.current().close()