#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from tornado.httpclient import HTTPClient,HTTPRequest
from tornado.ioloop import IOLoop
from tornado.curl_httpclient import AsyncHTTPClient
import pycurl
import base64

async def fn(url):
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    client = AsyncHTTPClient()
    request = HTTPRequest(
        url=url,
        proxy_host='http://http-pro.abuyun.com',
        proxy_port=9010,
        proxy_username='HWZ4K0025R7161XP',
        proxy_password='373904A5540BC8BA',
    )
    response = await client.fetch(request)
    return response.body

if __name__ == "__main__":
    from tornado.gen import concurrent
    result = IOLoop.current().run_sync(lambda : fn("http://mypics.zhaopin.com/pic/2016/6/13/90c4ee79-55d8-49b7-9fa6-4aad6da898dd.jpg"))
    
    print(base64.encodebytes(result).decode())

# import json
# import tornado.ioloop
# from tornado.httpclient import AsyncHTTPClient, HTTPRequest
# from tornado.concurrent import Future


# def futrue_callback(res_future):
#     print("调用回调函数 Futrue")
#     s = res_future.result().body.decode('gbk')
#     print(s)


# def async_fetch_future(url):
#     """
#     异步请求，使用Future类
#     :param url:
#     :return:
#     """
#     http_client = AsyncHTTPClient()
#     my_future = Future()
#     request = HTTPRequest(
#         url=url,
#         proxy_host='http://http-pro.abuyun.com:9010',
#         proxy_username='HWZ4K0025R7161XP',
#         proxy_password='373904A5540BC8BA',
#     )

#     fetch_future = http_client.fetch(request)
#     fetch_future.add_done_callback(
#         # Future的result默认为HttpResponce
#         lambda f: my_future.set_result(f.result()))
#     return my_future

# if __name__ == '__main__':
#     # 异步请求，返回Futrue类
#     s = async_fetch_future("http://mypics.zhaopin.com/pic/2016/6/13/90c4ee79-55d8-49b7-9fa6-4aad6da898dd.jpg")
#     io_loop = tornado.ioloop.IOLoop.current()
#     io_loop.add_future(s, callback=futrue_callback)
#     io_loop.start()


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

# import os
# import re
# import json
# from utils import strings

# if __name__ == '__main__':
#     # matches = re.search(r'(外资\(欧美\)|外资\(非欧美\)|合资|国企|民营公司|民营|上市公司|创业公司|外企代表处|政府机关|事业单位|非营利机构)', '民营dkdkddkk')
#     # print(matches.group())

#     filename = os.getcwd() + '/test/data/resume/zhaopin/6.html'
#     with open(filename, 'r') as f:
#         fileContext = f.read()
#         f.close()

#     post_args = strings.rpc_params({
#         'c': 'apis/logic_parse',
#         'm': 'parsers_engine',
#         'p': {
#             'site_id': 1,
#             'type': 1,
#             'body': fileContext,
#         }
#     })
#     print(json.dumps(post_args, ensure_ascii=False))
