#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# from tornado.httpclient import AsyncHTTPClient
# from tornado.ioloop import IOLoop

# async def fn(url):
#     client = AsyncHTTPClient()
#     response = await client.fetch(url)
#     return response.body

# if __name__ == "__main__":
#     from tornado.gen import concurrent
#     result = IOLoop.current().run_sync(lambda : fn("https://www.jianshu.com"))
#     print(str(result, 'utf-8'))

import json
import tornado.ioloop
from tornado.httpclient import AsyncHTTPClient
from tornado.concurrent import Future


def futrue_callback(res_future):
    print("调用回调函数 Futrue")
    s = res_future.result().body.decode('gbk')
    print(s)


def async_fetch_future(url):
    """
    异步请求，使用Future类
    :param url:
    :return:
    """
    http_client = AsyncHTTPClient()
    my_future = Future()
    fetch_future = http_client.fetch(url)
    fetch_future.add_done_callback(
        # Future的result默认为HttpResponce
        lambda f: my_future.set_result(f.result()))
    return my_future

if __name__ == '__main__':
    # 异步请求，返回Futrue类
    s = async_fetch_future("http://www.qq.com")
    io_loop = tornado.ioloop.IOLoop.current()
    io_loop.add_future(s, callback=futrue_callback)
    io_loop.start()


# async def http_curl(**kwargs):
#     from tornado.httpclient import AsyncHTTPClient,HTTPRequest,HTTPError
    
#     http_client = AsyncHTTPClient()
#     http_request = HTTPRequest(
#         url=kwargs['url'],
#     )

#     result = ""
#     try:
#         response = await AsyncHTTPClient().fetch(http_request)
#         result = str(response.body, 'utf-8')
#         print(result)
#     except HTTPError as e:
#         # HTTPError is raised for non-200 responses; the response
#         # can be found in e.response.
#         print("Error: " + str(e))
#     except Exception as e:
#         # Other errors are possible, such as IOError.
#         print("Error: " + str(e))
#     finally :
#         http_client.close()

#     return result


# if __name__ == "__main__":
#     from tornado.ioloop import IOLoop
#     IOLoop.instance().run_sync(lambda : http_curl(url="https://www.jianshu.com"))