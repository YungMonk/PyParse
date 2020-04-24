
import os

from lib import route
from model import parser_engine

class HelloTest(object):

    @route.router.route(url=r"/", method=route.router._GET)
    def home(self, req):
        return "hello world"



    def cv_parser(self):
        filename = os.getcwd() + '/test/carjob/1.html'
        with open(filename, 'r') as f:
            fileContext = f.read()
            f.close()

            obj = parser_engine.ParserEngine(51, fileContext, 1)
            obj.dispatch()