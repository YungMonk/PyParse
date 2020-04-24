#!/usr/bin/python3.8
# -*- coding: utf-8 -*-

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


if __name__ == '__main__':

    try:
        with socketserver.TCPServer(("", 8000), http_request_handler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print('^c received,shutting down the web server!')
