#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import IOLoop

url = "https://www.jianshu.com"

async def fn():
    client = AsyncHTTPClient()
    response = await client.fetch(url)
    print(response.body)

if __name__ == "__main__":
    IOLoop.current().run_sync(fn)