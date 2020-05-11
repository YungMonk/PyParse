
import os
import time

from lib import route,path
from model import parser_engine

class HelloTest(object):

    @route.router.route(url=r"/hello", method=route.router._POST | route.router._GET)
    def home(self, req):
        return "hello world"


    @route.router.route(url=r"/parse", method=route.router._POST | route.router._GET)
    def cv_parser(self, req):
        filename =  path._ROOT_PATH +'/test/carjob/1.html'
        print(filename)
        with open(filename, 'r') as f:
            fileContext = f.read()
            f.close()

            obj = parser_engine.ParserEngine(51, fileContext, 1)
            return obj.dispatch()